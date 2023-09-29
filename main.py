import random, sys

from GeneralDQN import DQN

from TennisEnv import TennisEnv
from TennisQNet import TennisLeaderQNetwork
from TennisQNet import TennisDealerQNetwork

if __name__ == "__main__":

    # Leader
    leader = DQN(TennisLeaderQNetwork)
    if len(sys.argv) > 1:
        leader.load_model(sys.argv[1])

    # Dealer
    dealer = DQN(TennisDealerQNetwork)
    if len(sys.argv) > 2:
        dealer.load_model(sys.argv[2])

    # Environment
    environment = TennisEnv(leader, dealer, rewarded_player="dealer")

    # Train the model
    dealer.train(environment)