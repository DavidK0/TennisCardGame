# This script allows you to train DQN models.
# You just need to make the environment and the Q-network

# Standard Library Imports
import random, math, datetime, os
from collections import namedtuple, deque
from itertools import count

# Thir- Party Library Imports
import torch
from torch.utils.tensorboard import SummaryWriter

# Check if GPU is available and set the device accordingly
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# random seed
SEED = 0
random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

class DQN():
    # Define a named tuple 'Transition' to represent a single transition in our environment.
    # It essentially maps (state, action) pairs to their (next_state, reward) result.
    Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))
    
    def __init__(self, qNetwork, hyperparameters):
        # Hyperparameters
        self.BATCH_SIZE = 200
        self.GAMMA = 0.99 # Discount for unknown future rewards
        self.LR = hyperparameters["LR"]
        self.EPS_START = 0.9 # The chance to make a random move
        self.EPS_END = 0.05
        self.EPS_DECAY = hyperparameters["EPS_DECAY"]
        self.GRAD_CLIP_MIN = -10
        self.GRAD_CLIP_MAX = 10
        self.TAU = 0.005 # The rate to update the target net
        self.MEMORY_LENGTH = 100000 # Maximim transitions to be remembered

        # Model settings
        self.TRAINEE = "dealer"
        self.steps_done = 0  
        self.eps_threshold = self.EPS_START

        # Initialize DQN models
        self.policy_net = qNetwork().to(device)
        self.target_net = qNetwork().to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        num_parameters = sum(p.numel() for p in self.policy_net.parameters() if p.requires_grad)
        print(f"Created a {qNetwork.__name__} model with {num_parameters} parameters")

        # Optimization and Memory
        self.optimizer = torch.optim.AdamW(self.policy_net.parameters(), lr=self.LR, amsgrad=True)
        self.memory = ReplayMemory(self.MEMORY_LENGTH)

        # Logging
        log_dir = "logs"
        current_time = datetime.datetime.now().strftime(f"log_{self.LR}_{self.EPS_DECAY}")
        log_dir = os.path.join(log_dir, current_time)
        self.summary_writer = SummaryWriter(log_dir=log_dir)

        # Validation
        self.running_rewards = RunningAverage(max_length=400)
        self.running_wins = RunningAverage(max_length=400)
        self.running_losses = RunningAverage(max_length=400)
        self.best_validation_score = float('-inf')
        self.VALIDATION_GAMES = 400
        self.VALIDATION_FREQUENCY = 1000
        self.checkpoint_save_name = None
        self.OUTPUT_PATH = "outputs"
        self.LJUST_LENGTH = 150

        # Early stopping
        self.PATIENCE = 1.5e+6
        self.counter = 0
        self.best_score = None
        self.stop = False

    # Main training loop to train the Q-network using the Tennis environment
    def train(self, environment, save_name, games=-1):
        self.checkpoint_save_name = save_name

        # Iterate over each episode
        #for i_episode in range(num_episodes):
        game = 0
        while game < games or games < 1:
            game += 1
            
            # Reset the environment and initialize variables
            state = environment.reset()

            # Iterate over each step in the episode
            for t in count():
                # Select an action based on the current state
                action = self.epsilon_greedy_policy(environment)
                
                # Take the selected action in the environment
                next_state, reward, done, exit_cond = environment.step(action.item())
                
                # If the episode is done, set the next state to None
                if done:
                    next_state = None

                # Store the transition in the replay memory
                self.memory.push(state.unsqueeze(0), action, next_state.unsqueeze(0) if next_state is not None else None, reward)
                
                # Move to the next state
                state = next_state

                # Optimize the Q-network based on the stored experiences
                self.optimize_model()
                
                # Soft update of the target network's weights
                target_net_state_dict = self.target_net.state_dict()
                policy_net_state_dict = self.policy_net.state_dict()
                for key in policy_net_state_dict:
                    target_net_state_dict[key] = policy_net_state_dict[key]*self.TAU + target_net_state_dict[key]*(1-self.TAU)
                self.target_net.load_state_dict(target_net_state_dict)

                # If the episode is done, stop
                if done:
                    break

            self.running_rewards.append(reward)
            if environment.winner == environment.rewarded_player:
                self.running_wins.append(1)
            else:
                self.running_wins.append(0)

            # Display the training progress
            progress_str = f"Training: {game % self.VALIDATION_FREQUENCY}/{self.VALIDATION_FREQUENCY}"
            print(progress_str.ljust(self.LJUST_LENGTH), end="\r")

            # Validation
            if game % self.VALIDATION_FREQUENCY == 0:
                val_wins, val_reward, val_loss = self.validate(environment)

                current_datetime = datetime.datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                wins_str = f"Avg Wins: {custom_round(val_wins, 3)}"
                reward_str = f"Avg reward: {custom_round(val_reward, 3)}"
                loss_str = f"Avg loss: {custom_round(val_loss, 3)}"
                step_str = f"Step: {self.steps_done}"
                eps_str = f"Eps threshold: {self.eps_threshold:.2%}"

                display_str = f"{formatted_datetime}, {wins_str}, {reward_str}, {loss_str}, {step_str}, {eps_str}"
                print(display_str.ljust(self.LJUST_LENGTH), end="")

                if val_reward > self.best_validation_score:
                    self.best_validation_score = val_reward
                    save_name = f"{self.checkpoint_save_name}_{self.LR}_{self.EPS_DECAY}"
                    self.save_model(os.path.join(self.OUTPUT_PATH, save_name))
                    print(f"\nNew best model found, saving to {save_name}", end="")
                print()
                
                # Early Stopping
                if self.best_score is None:
                    self.best_score = val_reward
                elif val_reward > self.best_score:  # Maximize reward
                    self.best_score = val_reward
                    self.counter = 0
                else:
                    self.counter += 1
                    if self.counter >= self.PATIENCE:
                        print("Early stopping triggered at step {self.steps_done}, no improvements after {self.PATIENCE}")
                        break

    # runs a few games with epsilon set to zero (no random moves)
    def validate(self, environment):
        total_wins = 0
        total_reward = 0
        total_loss = 0
        validation_steps = 0
        for v in range(self.VALIDATION_GAMES):
            print(f"Validating {v}/{self.VALIDATION_GAMES}".ljust(self.LJUST_LENGTH), end="\r")
            # Reset the environment and initialize variables
            environment.reset()

            # Iterate over each step in the episode
            for t in count():
                # Select an action based on the current state
                action = self.choose_action(environment)
                
                # Take the selected action in the environment
                next_state, reward, done, exit_cond = environment.step(action.item())
                
                # Get loss
                total_loss += self.optimize_model(optimize=False).item()
                
                
                # If the episode is done, stop
                if done:
                    validation_steps += t
                    total_reward += environment.reward
                    break

            # Track wins
            if environment.winner == environment.rewarded_player:
                total_wins += 1
        
        avg_wins = total_wins / self.VALIDATION_GAMES
        avg_reward = total_reward / self.VALIDATION_GAMES
        avg_loss = total_loss / validation_steps
        self.summary_writer.add_scalar("Val win rate", avg_wins, self.steps_done)
        self.summary_writer.add_scalar("Val reward", avg_reward, self.steps_done)
        self.summary_writer.add_scalar("Epsilon threshold", self.eps_threshold, self.steps_done)
        self.summary_writer.add_scalar("Loss", avg_loss, self.steps_done)
        return avg_wins, avg_reward, avg_loss
        
    def optimize_model(self, optimize=True):
        """
        Optimize the Q-network based on the stored experiences in the replay memory.
        
        This function samples a batch of transitions from the memory, computes the Q-values for the 
        current states and actions, calculates the expected Q-values based on the next states and rewards,
        and then updates the Q-network using the Huber loss between the computed and expected Q-values.
        """
        # If there aren't enough samples in the memory, return without doing anything
        if len(self.memory) < self.BATCH_SIZE:
            return

        # Sample a batch of transitions from the memory
        transitions = self.memory.sample(self.BATCH_SIZE)
        batch = DQN.Transition(*zip(*transitions))

        # Create a mask of non-final states (states that are not terminal)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
        state_batch = torch.cat(batch.state, dim=0).to(device)
        action_batch = torch.cat(batch.action).to(device)
        reward_batch = torch.tensor(batch.reward, device=device, dtype=torch.float32)

        # Compute the Q-values for the current states and actions
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Compute the maximum Q-value for the next states (used in Q-learning)
        next_state_values = torch.zeros(self.BATCH_SIZE, device=device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()
        
        # Compute the expected Q-values based on the rewards and future Q-values
        expected_state_action_values = (next_state_values * self.GAMMA) + reward_batch

        # Compute the Huber loss between the current and expected Q-values
        loss = torch.nn.functional.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))


        # Add loss to running_losses and remove oldest if exceeds maxlen
        self.running_losses.append(loss.item())

        # Backpropagate the loss and optimize the Q-network
        if optimize:
            self.optimizer.zero_grad()
            loss.backward()
            for param in self.policy_net.parameters():
                param.grad.data.clamp_(self.GRAD_CLIP_MIN, self.GRAD_CLIP_MAX)
            self.optimizer.step()

        return loss
    
    def epsilon_greedy_policy(self, environment):
        """
        Select an action based on the current state using epsilon-greedy policy.
        
        Args:
        - state (torch.Tensor): The current state of the environment.
        - explote: False if you want to always use the model (and never random moves)
        
        Returns:
        - torch.Tensor: The selected action.
        """
        sample = random.random()  # Randomly sample a value between 0 and 1
        # Calculate the current epsilon threshold based on the number of steps taken
        self.eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * math.exp(-1. * self.steps_done / self.EPS_DECAY)
        self.steps_done += 1
        
        legal_moves = environment.get_legal_moves() # Get the list of legal moves
        
        # If the sampled value is greater than the threshold, select the best action based on the Q-values.
        if sample > self.eps_threshold:
            return self.choose_action(environment)
        else:
            # Select a random action from the set of legal moves
            move_index = environment.action_space.index(random.choice(legal_moves))
            return torch.tensor([[move_index]], device=device, dtype=torch.long)
        
    # return the best legal action from the current environment
    def choose_action(self, env):
        state_tensor = env.get_current_state().unsqueeze(0).to(device) # Convert the state to a tensor and add a batch dimension
        legal_moves = env.get_legal_moves() # Get the list of legal moves
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
            # Mask the Q-values of illegal moves
            for i in range(len(env.action_space) ):
                if i not in [env.action_space.index(card) for card in legal_moves]:
                    q_values[0][i] = -float('inf')
            return q_values.max(1)[1].view(1, 1)
    
    def load_model(self, policy_path=None, target_path=None):
        """Load a model from the given name."""
        if not policy_path:
            return

        try:
            policy_state_dict = torch.load(policy_path, map_location=device)
            self.policy_net.load_state_dict(policy_state_dict)
            print(f"Loaded policy network from {policy_path}")
        except Exception as e:
            print(f"Error loading model from {policy_path}: {e}")
        
        if target_path:
            try:
                target_state_dict = torch.load(target_path, map_location=device)
                print(f"Loaded target network from {target_path}")
                self.target_net.load_state_dict(target_state_dict )
            except Exception as e:
                print(f"Error loading model from {target_path}: {e}")
        else:
            self.target_net.load_state_dict(policy_state_dict)

    def save_model(self, model_name):
        """Save the policy network with the given name."""
        try:
            torch.save(self.policy_net.state_dict(), model_name + "_policy.pt")
            torch.save(self.target_net.state_dict(), model_name + "_target.pt")
        except Exception as e:
            print(f"Error saving model to {model_name}: {e}")

# A class to store and manage transitions in reinforcement learning.
class ReplayMemory(object):
    def __init__(self, capacity): # Initialize the ReplayMemory with a given capacity.
        self.memory = deque([], maxlen=capacity)
    def push(self, *args): # Store a new transition in the memory.
        self.memory.append(DQN.Transition(*args))
    def sample(self, batch_size): # Randomly sample a batch of transitions from the memory.
        return random.sample(self.memory, batch_size)
    def __len__(self): # Return the number of stored transitions in the memory.
        return len(self.memory)

def custom_round(number, digits=2):
    if not number or number == 0:
        return "0.0"

    abs_num = abs(number)
    exponent = 0

    if abs_num >= 1:
        while abs_num >= 10:
            abs_num /= 10
            exponent += 1
    else:
        while abs_num < 1:
            abs_num *= 10
            exponent -= 1

    if exponent >= 0:
        if exponent >= digits:
            rounded_num = round(number / (10 ** exponent), digits - 1)
            return f"{rounded_num:.{digits - 1}e}"
        else:
            rounded_num = round(number, digits - 1 - exponent)
            return f"{rounded_num}"
    else:
        total_digits = digits - exponent - 1
        rounded_num = round(number, total_digits)
        return f"{rounded_num:.{total_digits}f}"

# This class keeps track of a running average
class RunningAverage:
    def __init__(self, max_length):
        self.values = []
        self.max_length = max_length
     
    # add one or more items
    def append(self, values):
        # add new values
        if isinstance(values, list):
            self.values.extend(values)
        else:
            self.values.append(values)
        
        # remove old values
        self.values = self.values[-self.max_length:]
    
    # get the current average
    def get(self):
        if not self.values or len(self.values) == 0:
            return None
            
        return sum(self.values) / len(self.values)
