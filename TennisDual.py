# This scirpt pits two Tennis players against each other

import random

import Tennis
from Tennis import RandomTennisPlayer
from TennisLeaders import *
from TennisDealers import *

import scipy.stats

# The two players
leader = MySecondSmartLeader
dealer = MyFirstSmartDealer

# The numer of pairs of rounds to play
num_rounds = 1000

verbose = False

# track stats
p1_bids = [0, 0]
p1_wins = [0, 0]
p1_errors = [0, 0]

p2_bids = [0, 0]
p2_wins = [0, 0]
p2_errors = [0, 0]

p1_round_wins = 0
p2_round_wins = 0

# takes two lists of number, each with length 2, and adds them element wise
def add_number_pairs(number_pair1, number_pair2):
    return [number_pair1[0] + number_pair2[0], number_pair1[1] + number_pair2[1]]

#for trump_suit in [None]:
for round in range(num_rounds):
    print(f"Playing rounds: {round/num_rounds:.1%}", end="\r")
    trump_suit = random.choice(["S","C","D","H",None])
    round_info = Tennis.PlayTennisRound(leader, dealer, trump_suit, verbose)

    # track stats
    p1_bids = add_number_pairs(p1_bids, round_info[0][0][0])
    p1_wins = add_number_pairs(p1_wins, round_info[0][0][1])
    p1_errors = add_number_pairs(p1_errors, round_info[0][0][2])
    
    p2_bids = add_number_pairs(p2_bids, round_info[0][1][0])
    p2_wins = add_number_pairs(p2_wins, round_info[0][1][1])
    p2_errors = add_number_pairs(p2_errors, round_info[0][1][2])
    
    if round_info[1] == 0:
        p1_round_wins += 1
    elif round_info[1] == 1:
        p2_round_wins += 1

# print stats
def nice_format(num_pair, factor=1):
    return [f"{(x / (num_rounds / factor)):.1f}" for x in num_pair]

print(f"* {leader.__name__} *")
print(f"Average bids: {nice_format(p1_bids)}")
print(f"Average wins: {nice_format(p1_wins)}")
print(f"Average errors: {nice_format(p1_errors)}")
print()
print(f"* {dealer.__name__} *")
print(f"Average bids: {nice_format(p2_bids)}")
print(f"Average wins: {nice_format(p2_wins)}")
print(f"Average errors: {nice_format(p2_errors)}")
print()
print(f"Leader win rate: {p1_round_wins/num_rounds:.1%}")
print(f"Dealer win rate: {p2_round_wins/num_rounds:.1%}")
print(f"Tie rate: {(num_rounds-p1_round_wins-p2_round_wins)/num_rounds:.1%}")