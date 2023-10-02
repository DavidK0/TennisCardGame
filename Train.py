import argparse

from GeneralDQN import DQN

from TennisEnv import TennisEnv
from TennisQNet import TennisLeaderQNetwork
from TennisQNet import TennisDealerQNetwork

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--leader", default=None, help="The leader model (.pt) (optional)")
    parser.add_argument("--dealer", default=None, help="The dealer model (.pt) (optional)")
    parser.add_argument("--trainee", default="leader", help="\"dealer\" or \"leader\"")
    args = parser.parse_args()

    assert(args.trainee in ["leader", "dealer"])

    # Leader
    leader = DQN(TennisLeaderQNetwork)
    if args.leader:
        leader.load_model(args.leader)
        print("Loading leader model")

    # Dealer
    dealer = DQN(TennisDealerQNetwork)
    if args.dealer:
        dealer.load_model(args.dealer)
        print("Loading dealer model")

    # Environment
    environment = TennisEnv(leader, dealer, rewarded_player=args.trainee)

    # Train the model
    if args.trainee == "leader":
        leader.train(environment)
    else:
        dealer.train(environment)