# This scirpt pits two Tennis players against each other

import random

import Tennis
from Tennis import RandomTennisPlayer

import scipy.stats

# The two players
leader = RandomTennisPlayer
dealer = RandomTennisPlayer

# The numer of pairs of rounds to play
num_rounds = 100

verbose = False

# track stats
leader_bids = [0, 0]
leader_wins = [0, 0]
leader_errors = [0, 0]

dealer_bids = [0, 0]
dealer_wins = [0, 0]
dealer_errors = [0, 0]

leader_round_wins = 0
dealer_round_wins = 0

# takes two lists of number, each with length 2, and adds them element wise
def add_number_pairs(number_pair1, number_pair2):
    return [number_pair1[0] + number_pair2[0], number_pair1[1] + number_pair2[1]]

#for trump_suit in [None]:
for round in range(num_rounds):
    print(f"Playing rounds: {round/num_rounds:.1%}", end="\r")
    trump_suit = random.choice(["S","C","D","H",None])
    round_info = Tennis.PlayTennisRound(leader, dealer, trump_suit, verbose)

    # track stats
    leader_bids = add_number_pairs(leader_bids, round_info[0][0][0])
    leader_wins = add_number_pairs(leader_wins, round_info[0][0][1])
    leader_errors = add_number_pairs(leader_errors, round_info[0][0][2])
    
    dealer_bids = add_number_pairs(dealer_bids, round_info[0][1][0])
    dealer_wins = add_number_pairs(dealer_wins, round_info[0][1][1])
    dealer_errors = add_number_pairs(dealer_errors, round_info[0][1][2])
    
    if round_info[1] == 0:
        leader_round_wins += 1
    elif round_info[1] == 1:
        dealer_round_wins += 1

# print stats
def nice_format(num_pair, factor=1):
    return [f"{(x / (num_rounds / factor)):.1f}" for x in num_pair]

print(f"Results of {num_rounds:,} rounds")
print(f"Tie rate: {(num_rounds-leader_round_wins-dealer_round_wins)/num_rounds:.1%}")
print()
print(f"Leader: {leader.__name__}".ljust(30))
print(f"Wn rate: {leader_round_wins/num_rounds:.1%}")
print(f"Average bids: {nice_format(leader_bids)}")
print(f"Average wins: {nice_format(leader_wins)}")
print(f"Average errors: {nice_format(leader_errors)}")
print()
print(f"Dealer: {dealer.__name__}".ljust(30))
print(f"Win rate: {dealer_round_wins/num_rounds:.1%}")
print(f"Average bids: {nice_format(dealer_bids)}")
print(f"Average wins: {nice_format(dealer_wins)}")
print(f"Average errors: {nice_format(dealer_errors)}")