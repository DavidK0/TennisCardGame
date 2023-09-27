import sys
from Tennis import TennisEnv
from TennisRL import TennisLeaderQNetwork
from GeneralDQN import DQN

# Create the DQN agent
DQN = DQN(TennisEnv, TennisLeaderQNetwork, trump_suit=None)

num_games = 300

total_reward = 0  # Initialize the total reward to zero

# Load a model if it is provided
if len(sys.argv) > 1:
    DQN.load_model(sys.argv[1])

# Track wins and loses
games_won = 0
games_lost = 0
games_tied = 0

# Play many games
for i in range(num_games):
    # Print the progress of the current game
    print(f"Progress {(i + 1)/num_games:.1%}", end="\r")
        
    # Reset the environment for a new game
    DQN.env.reset()
    
    while not DQN.env.done:
        DQN.env.step(DQN.choose_action())  # Leader
        
    total_reward += DQN.env.reward # Accumulate the reward

    # Track wins and loses
    if DQN.env.winner == "leader":
        games_won += 1
    elif DQN.env.winner == "dealer":
        games_lost += 1
    else:
        games_tied += 1

# Calculate and print the average reward
average_reward = total_reward / num_games
win_rate = games_won / num_games
lose_rate = games_lost / num_games
tie_rate = games_tied / num_games
print(f"Average error difference over {num_games} games: {12*average_reward:.3f} (positive is good)")
print(f"Win/lose/tie rate: {win_rate:.1%}/{lose_rate:.1%}/{tie_rate:.1%}")