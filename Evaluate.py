import sys
from TennisEnv import TennisEnv
from TennisQNet import TennisLeaderQNetwork
from TennisQNet import TennisDealerQNetwork
from GeneralDQN import DQN

# Leader
leader = DQN(TennisLeaderQNetwork)
if len(sys.argv) > 1:
    leader.load_model(sys.argv[1])
    print("Loading leader model")

# Dealer
dealer = DQN(TennisDealerQNetwork)
if len(sys.argv) > 2:
    dealer.load_model(sys.argv[2])
    print("Loading dealer model")

# Environment
environment = TennisEnv(leader, dealer, rewarded_player="leader")

num_games = 5000

total_reward = 0  # Initialize the total reward to zero

# Track wins and loses
leader_wins = 0
dealer_wins = 0
games_tied = 0

# Play many games
for i in range(num_games):
    # Print the progress of the current game
    print(f"Progress {(i + 1)/num_games:.1%}", end="\r")
        
    # Reset the environment for a new game
    environment.reset()

    while True:
        # Leader
        leader_action = leader.choose_action(environment)
        environment.step_helper(leader_action)
        if environment.done:
            break

        # Dealer
        dealer_action = dealer.choose_action(environment)
        environment.step_helper(dealer_action)
        if environment.done:
            break
        
    total_reward += environment.reward # Accumulate the reward

    # Track wins and loses
    if environment.winner == "leader":
        leader_wins += 1
    elif environment.winner == "dealer":
        dealer_wins += 1
    else:
        games_tied += 1

# Calculate and print the average reward
average_reward = total_reward / num_games
leader_win_rate = leader_wins / num_games
dealer_win_rate = dealer_wins / num_games
tie_rate = games_tied / num_games
print(f"Average error difference over {num_games} games: {12*average_reward:.3f} (positive is good)")
print(f"Leader win/dealer win/tie rate: {leader_win_rate:.1%}/{dealer_win_rate:.1%}/{tie_rate:.1%}")