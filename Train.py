import argparse

from GeneralDQN import DQN

from TennisEnv import TennisEnv
from TennisQNet import TennisLeaderQNetwork
from TennisQNet import TennisDealerQNetwork

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--leader", default=None, help="The leader policy network (.pt) (optional)")
    parser.add_argument("--leader_target", default=None, help="The leader target network (.pt) (optional)")
    parser.add_argument("--dealer", default=None, help="The dealer policy network (.pt) (optional)")
    parser.add_argument("--dealer_target", default=None, help="The dealer target network(.pt) (optional)")
    parser.add_argument("--trainee", default="leader", help="\"dealer\" or \"leader\"")
    parser.add_argument("--save_name", default="best", help="Path to save checkpoints to")
    args = parser.parse_args()

    assert(args.trainee in ["leader", "dealer"])



    learning_rates = [1e-3, 5e-4, 1e-4, 5e-5, 1e-5]
    epsilon_decays = [1e5, 5e5, 1e6, 5e6]
    for lr in learning_rates:
        for eps_decay in epsilon_decays:
            hyperparameters = {"LR": lr, "EPS_DECAY": eps_decay}

            # Leader
            leader = DQN(TennisLeaderQNetwork, hyperparameters)
            leader.load_model(args.leader, args.leader_target)

            # Dealer
            dealer = DQN(TennisDealerQNetwork, hyperparameters)
            dealer.load_model(args.dealer, args.dealer_target)

            # Environment
            environment = TennisEnv(leader, dealer, rewarded_player=args.trainee)

            # Train just one player at a time
            if args.trainee == "leader":
                trainee_obj = leader
            else:
                trainee_obj = dealer

            # Train the model
            trainee_obj.train(environment, save_name=args.save_name)

            # Validate
            avg_reward = trainee_obj.validate(environment)

            # Print results
            print("Learning rate: {lr}, Epsilon decay: {eps_decay}, Average reward: {avg_reward}")