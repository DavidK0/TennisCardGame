from Tennis import TennisEnv
from TennisRL import TennisLeaderQNetwork
from GeneralDQN import DQN

# Create the DQN agent
DQN = DQN(TennisEnv, TennisLeaderQNetwork, trump_suit=None)

num_games = 1
total_reward = 0  # Initialize the total reward to zero

# Play many games
for i in range(num_games):
    # Print the progress of the current game
    print(f"Progress {(i + 1)/num_games:.1%}", end="\r")
        
    # Reset the environment for a new game
    DQN.env.reset()
    
    while not DQN.env.done:
        DQN.env.step(DQN.choose_action())  # Leader
        
    total_reward += DQN.env.reward  # Accumulate the reward

# Calculate and print the average reward
average_reward = total_reward / num_games
print(f"Average Reward over {num_games} games: {average_reward:.3f}")