# This scirpt pits two players against each other

import Tennis

from TennisPlayers import RandomTennisPlayer
from TennisPlayers import AverageBidRandomPlayer
from TennisPlayers import AgressivePlayer

# takes two lists of number, each with length 2, and adds them element wise
def add_number_pairs(number_pair1, number_pair2):
    return [number_pair1[0] + number_pair2[0], number_pair1[1] + number_pair2[1]]

if __name__ == "__main__":
    player1 = AverageBidRandomPlayer
    player2 = AgressivePlayer

    # the numer of pairs of rounds to play
    num_round_pairs = 10000

    # track stats
    p1_bids = [0, 0]
    p1_wins = [0, 0]
    p1_errors = [0, 0]
    
    p1_as_leader_bids = [0, 0]
    p1_as_leader_wins = [0, 0]
    p1_as_leader_errors = [0, 0]
    
    p1_as_dealer_bids = [0, 0]
    p1_as_dealer_wins = [0, 0]
    p1_as_dealer_errors = [0, 0]

    p2_bids = [0, 0]
    p2_wins = [0, 0]
    p2_errors = [0, 0]
    
    p2_as_leader_bids = [0, 0]
    p2_as_leader_wins = [0, 0]
    p2_as_leader_errors = [0, 0]
    
    p2_as_dealer_bids = [0, 0]
    p2_as_dealer_wins = [0, 0]
    p2_as_dealer_errors = [0, 0]

    leader_bids = [0, 0]
    leader_wins = [0, 0]
    leader_errors = [0, 0]

    dealer_bids = [0, 0]
    dealer_wins = [0, 0]
    dealer_errors = [0, 0]

    p1_round_wins = 0
    p2_round_wins = 0
    leader_round_wins = 0
    dealer_round_wins = 0

    #for trump_suit in [None]:
    for round in range(num_round_pairs):
        print(f"Playing rounds: {round/num_round_pairs:.1%}", end="\r")
        trump_suit = None
        round1_info, round2_info = Tennis.PlayTwoRounds(player1, player2, trump_suit, False)

        # track stats
        rounds = [round1_info, round2_info]
        #print(rounds[0])
        for i in range(2):
            p1_bids = add_number_pairs(p1_bids, rounds[i][0][i][0])
            p1_wins = add_number_pairs(p1_wins, rounds[i][0][i][1])
            p1_errors = add_number_pairs(p1_errors, rounds[i][0][i][2])
            
            p2_bids = add_number_pairs(p2_bids, rounds[i][0][1-i][0])
            p2_wins = add_number_pairs(p2_wins, rounds[i][0][1-i][1])
            p2_errors = add_number_pairs(p2_errors, rounds[i][0][1-i][2])
            
            if i == 0:
                p1_as_leader_bids = add_number_pairs(p1_as_leader_bids, rounds[i][0][0][0])
                p1_as_leader_wins = add_number_pairs(p1_as_leader_wins, rounds[i][0][0][1])
                p1_as_leader_errors = add_number_pairs(p1_as_leader_errors, rounds[i][0][0][2])
                
                p2_as_dealer_bids = add_number_pairs(p2_as_dealer_bids, rounds[i][0][1][0])
                p2_as_dealer_wins = add_number_pairs(p2_as_dealer_wins, rounds[i][0][1][1])
                p2_as_dealer_errors = add_number_pairs(p2_as_dealer_errors, rounds[i][0][1][2])
            else:
                p2_as_leader_bids = add_number_pairs(p2_as_leader_bids, rounds[i][0][0][0])
                p2_as_leader_wins = add_number_pairs(p2_as_leader_wins, rounds[i][0][0][1])
                p2_as_leader_errors = add_number_pairs(p2_as_leader_errors, rounds[i][0][0][2])
                
                p1_as_dealer_bids = add_number_pairs(p1_as_dealer_bids, rounds[i][0][1][0])
                p1_as_dealer_wins = add_number_pairs(p1_as_dealer_wins, rounds[i][0][1][1])
                p1_as_dealer_errors = add_number_pairs(p1_as_dealer_errors, rounds[i][0][1][2])

            leader_bids = add_number_pairs(leader_bids, rounds[i][0][0][0])
            leader_wins = add_number_pairs(leader_wins, rounds[i][0][0][1])
            leader_errors = add_number_pairs(leader_errors, rounds[i][0][0][2])
            
            dealer_bids = add_number_pairs(dealer_bids, rounds[i][0][1][0])
            dealer_wins = add_number_pairs(dealer_wins, rounds[i][0][1][1])
            dealer_errors = add_number_pairs(dealer_errors, rounds[i][0][1][2])

            if i == 0:
                if rounds[i][1] == 0:
                    p1_round_wins += 1
                    leader_round_wins += 1
                elif rounds[i][1] == 1:
                    p2_round_wins += 1
                    dealer_round_wins += 1
            else:
                if rounds[i][1] == 0:
                    p2_round_wins += 1
                    leader_round_wins += 1
                elif rounds[i][1] == 1:
                    p1_round_wins += 1
                    dealer_round_wins += 1

    # print stats
    def nice_format(num_pair, factor=1):
        return [f"{(x / (total_rounds / factor)):.1f}" for x in num_pair]

    total_rounds = num_round_pairs * 2
    print("\n")
    print(player1.__name__)
    print()
    print(f"average p1 bids: {nice_format(p1_bids)}")
    print(f"average p1 wins: {nice_format(p1_wins)}")
    print(f"average p1 errors: {nice_format(p1_errors)}")
    print()
    print(f"average p1 as leader bids: {nice_format(p1_as_leader_bids, 2)}")
    print(f"average p1 as leader wins: {nice_format(p1_as_leader_wins, 2)}")
    print(f"average p1 as leader errors: {nice_format(p1_as_leader_errors, 2)}")
    print()
    print(f"average p1 as dealer bids: {nice_format(p1_as_dealer_bids, 2)}")
    print(f"average p1 as dealer wins: {nice_format(p1_as_dealer_wins, 2)}")
    print(f"average p1 as dealer errors: {nice_format(p1_as_dealer_errors, 2)}")
    print()
    print(player2.__name__)
    print()
    print(f"average p2 bids: {nice_format(p2_bids)}")
    print(f"average p2 wins: {nice_format(p2_wins)}")
    print(f"average p2 errors: {nice_format(p2_errors)}")
    print()
    print(f"average p2 as leader bids: {nice_format(p2_as_leader_bids, 2)}")
    print(f"average p2 as leader wins: {nice_format(p2_as_leader_wins, 2)}")
    print(f"average p2 as leader errors: {nice_format(p2_as_leader_errors, 2)}")
    print()
    print(f"average p2 as dealer bids: {nice_format(p2_as_dealer_bids, 2)}")
    print(f"average p2 as dealer wins: {nice_format(p2_as_dealer_wins, 2)}")
    print(f"average p2 as dealer errors: {nice_format(p2_as_dealer_errors, 2)}")
    print()
    print(f"average leader bids: {nice_format(leader_bids)}")
    print(f"average leader wins: {nice_format(leader_wins)}")
    print(f"average leader errors: {nice_format(leader_errors)}")
    print()
    print(f"average dealer bids: {nice_format(dealer_bids)}")
    print(f"average dealer wins: {nice_format(dealer_wins)}")
    print(f"average dealer errors: {nice_format(dealer_errors)}")
    print()
    print(f"p1 win rate: {p1_round_wins/total_rounds:.1%}")
    print(f"p2 win rate: {p2_round_wins/total_rounds:.1%}")
    print(f"leader win rate: {leader_round_wins/total_rounds:.1%}")
    print(f"dealer win rate: {dealer_round_wins/total_rounds:.1%}")
    print(f"tie rate: {(total_rounds-p1_round_wins-p2_round_wins)/total_rounds:.1%}")