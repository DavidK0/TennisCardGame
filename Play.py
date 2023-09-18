# Use this script to play Tennis against a trained agent via the command line.

# Standard Library Imports
import random, math, re
import torch

# Local Library Imports
from Tennis import TennisEnv #  The environment in which the RL agent interacts.
from TennisRL import DQNTennis
from Deck import Card

# Load the trained agent model
MODEL_LOAD_PATH = 'latest_dqn_tennis_model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
policy_net = DQNTennis().to(device)
policy_net.load_state_dict(torch.load(MODEL_LOAD_PATH))
policy_net.eval()

def select_action(env):
    """
    Select an action based on the current state using the trained agent.
    """
    state_tensor = env.get_current_state().unsqueeze(0).to(device)
    with torch.no_grad():
        q_values = policy_net(state_tensor)
        
        # Get the list of legal moves
        legal_moves = env.get_legal_moves()
        
        # Mask the Q-values of illegal moves
        for i in range(len(env.action_space)):
            if i not in [env.action_space.index(card) for card in legal_moves]:
                q_values[0][i] = -float('inf')
                
        return q_values.max(1)[1].view(1, 1)


def human_play():
    """
    Let a human player play tennis against a trained agent.
    """
    # Initialize the Tennis environment with no specific trump suit
    env = TennisEnv(trump_suit=None)
    
    # Reset the environment and initialize variables
    state = env.reset()

    def str_to_card(card_string):
        # Define a regular expression pattern to match valid playing card strings
        pattern = r'^[2-tjqkaTJQKA][cdhsCDHS]$'
        
        # Use re.match to check if the card_string matches the pattern
        if not re.match(pattern, card_string):
            return None
        
        # Extract the suit and rank from the valid card string
        rank = card_string[:-1].upper()
        suit = card_string[-1].upper()  # Convert to lowercase for consistency
        
        return Card(rank, suit)
    
    while True:
        # Display the current state to the human player
        print(env.render())
        
        # Get the list of legal actions
        legal_actions = env.get_legal_moves()
        
        # Ask the human player for their move
        card_str = input("Enter your move (e.g., 'jc' for jack of clubs): ")
        card = str_to_card(card_str)

        # Ensure the action is legal and valid
        while card is None or card not in legal_actions:
            # Ask the human player for their move
            card_str = input("Enter your move (e.g., 'jc' for jack of clubs): ")
            card = str_to_card(card_str)
        
        action = env.action_space.index(card)
        
        # Take the human player's action in the environment
        next_state, reward, done, _ = env.step(action)
        
        # If the game is over after the human player's move, end the game
        if done:
            print("Game Over! Your Reward:", reward)
            break
        
        # Agent's move
        agent_action = select_action(env)
        agent_card = env.action_space[agent_action.item()]
        print("Agent's Move:", agent_card, "\n")
        
        # Take the agent's action in the environment
        next_state, reward, done, _ = env.step(agent_action.item())
        
        # If the game is over after the agent's move, end the game
        if done:
            print("Game Over! Your Reward:", reward)
            break
        
        # Update the current state
        state = next_state

# Call the function to start the game
human_play()