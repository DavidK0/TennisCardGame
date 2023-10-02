# This script allows one to train DQN models.
# You just need to make the environment and the Q-network

# Standard Library Imports
import random, math, datetime, re
from collections import namedtuple, deque
from itertools import count

import torch

# Check if GPU is available and set the device accordingly
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

SEED = 0
random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

class DQN():
    # Define a named tuple 'Transition' to represent a single transition in our environment.
    # It essentially maps (state, action) pairs to their (next_state, reward) result.
    Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))
    
    def __init__(self, qNetwork):
        # Define hyperparameters for the DQN training
        self.BATCH_SIZE = 128  # Size of the batch sampled from the replay memory
        self.GAMMA = 0.99  # Discount factor for future rewards
        self.LR = 1e-5  # Learning rate for the optimizer
        self.EPS_START = 0.1  # Starting value of epsilon for epsilon-greedy action selection
        self.EPS_END = 0.1  # Minimum value of epsilon
        self.EPS_DECAY = 800000  # Decay rate for epsilon
        self.GRAD_CLIP_MIN = -10
        self.GRAD_CLIP_MAX = 10
        self.TAU = 0.005  # The factor for soft-updating the target network weights

        self.eps_threshold = self.EPS_START

        # Initialize the policy and target DQN models
        self.policy_net = qNetwork().to(device)
        self.target_net = qNetwork().to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())  # Initialize the target network with the policy network's weights

        # Define the optimizer for training the policy network
        self.optimizer = torch.optim.AdamW(self.policy_net.parameters(), lr=self.LR, amsgrad=True)
        
        self.steps_done = 0  
        
        # Initialize the replay memory of transitions
        self.memory = ReplayMemory(100000)
        
        self.running_maxlen = 1000
        self.running_rewards = []
        self.running_wins = []
        self.running_losses = []

    # Main training loop to train the Q-network using the Tennis environment
    def train(self, environment):
        # Iterate over each episode
        #for i_episode in range(num_episodes):
        while True:
            # Display the training progress
            if len(self.running_rewards) > 0 and len(self.running_losses) > 0:
                avg_reward = sum(self.running_rewards) / len(self.running_rewards)
                avg_wins = sum(self.running_wins) / len(self.running_wins)
                avg_loss = sum(self.running_losses) / len(self.running_losses)
            else:
                avg_reward, avg_wins, avg_loss = 0, 0, 0

            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            display_str = f"{formatted_datetime}, Avg reward: {custom_round(avg_reward, 3)}, Avg Wins: {custom_round(avg_wins, 3)}, Avg loss: {custom_round(avg_loss, 3)}, Step: {self.steps_done}, Eps threshold: {self.eps_threshold:.3%}"
            display_str_plus_games = display_str + f", Game: {len(self.running_rewards)}/{self.running_maxlen}"
            print(display_str_plus_games.ljust(150), end="\r")
            if len(self.running_rewards) >= self.running_maxlen:
                self.running_rewards = []
                self.running_wins = []
                self.running_losses = []
                
                print(display_str.ljust(150))


                # Save the latest model
                #filename_datetime = re.sub(r'[\/:*?"<>| ]', '_', formatted_datetime)
                #filename_datetime = re.sub(r'[\/:*?"<>| ]', '_', formatted_datetime)
                #self.save_model(f"outputs/{filename_datetime}_{avg_reward:.2f}_{avg_loss:.2f}.pth")

            
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
            if environment.winner == "dealer":
                self.running_wins.append(1)
            else:
                self.running_wins.append(0)
        
    def optimize_model(self):
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
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(self.GRAD_CLIP_MIN, self.GRAD_CLIP_MAX)
        self.optimizer.step()
    
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
    
    def load_model(self, path):
        """Load a model from the given path."""
        try:
            state_dict = torch.load(path, map_location=device)
            self.policy_net.load_state_dict(state_dict)
            #self.target_net.load_state_dict(state_dict)
        except Exception as e:
            print(f"Error loading model from {path}: {e}")

    def save_model(self, path):
        """Save the policy network to the given path."""
        try:
            torch.save(self.policy_net.state_dict(), path)
        except Exception as e:
            print(f"Error saving model to {path}: {e}")

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

def chi_squared_test(old_win, old_lose, old_draw, new_win, new_lose, new_draw):
    # Row and Column Totals
    row1_total = old_win + old_lose + old_draw
    row2_total = new_win + new_lose + new_draw
    col1_total = old_win + new_win
    col2_total = old_lose + new_lose
    col3_total = old_draw + new_draw
    grand_total = row1_total + row2_total
    
    # Expected Frequencies
    exp_old_win = (row1_total * col1_total) / grand_total
    exp_old_lose = (row1_total * col2_total) / grand_total
    exp_old_draw = (row1_total * col3_total) / grand_total
    
    exp_new_win = (row2_total * col1_total) / grand_total
    exp_new_lose = (row2_total * col2_total) / grand_total
    exp_new_draw = (row2_total * col3_total) / grand_total
    
    # Chi-Squared Value
    chi_squared = ((old_win - exp_old_win)**2 / exp_old_win) + \
                  ((old_lose - exp_old_lose)**2 / exp_old_lose) + \
                  ((old_draw - exp_old_draw)**2 / exp_old_draw) + \
                  ((new_win - exp_new_win)**2 / exp_new_win) + \
                  ((new_lose - exp_new_lose)**2 / exp_new_lose) + \
                  ((new_draw - exp_new_draw)**2 / exp_new_draw)
    
    # Degrees of Freedom
    dof = (2 - 1) * (3 - 1)
    
    # Critical Value (alpha=0.05)
    critical_value = chi2.ppf(0.95, dof)
    
    # Test Conclusion
    if chi_squared > critical_value:
        return f"The change in win rates is statistically significant. Chi-Squared: {chi_squared}, Critical Value: {critical_value}"
    else:
        return f"The change in win rates is not statistically significant. Chi-Squared: {chi_squared}, Critical Value: {critical_value}"

def custom_round(number, digits=2):
    if number == 0:
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