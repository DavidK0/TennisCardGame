# This script runs a round robin tournament

import random

import Tennis
from Tennis import RandomTennisPlayer
from TennisLeaders import *
from TennisDealers import *

if __name__ == "__main__":
    num_tournaments = 100
    
    # Load the leaders
    leaders = [RandomTennisPlayer, AverageBidRandomLeader, AgressiveLeader, MyFirstSmartLeader,
        MySecondSmartLeader]
    
    # Load the dealers
    dealers = [RandomTennisPlayer, AverageBidRandomDealer, AgressiveDealer, PassiveDealer,
        MyFirstSmartDealer]  

    # A 3D array
    outcomes = []
    total_iterations = len(leaders) * len(dealers) * num_tournaments
    current_iteration = 0
    for leader_index in range(len(leaders)):
        outcomes.append([])
        for dealer_index in range(len(dealers)):
            outcomes[-1].append([0 ,0])
            for i in range(num_tournaments):
                current_iteration += 1
                progress = current_iteration / total_iterations
                print(f"Progress: {progress:.1%}", end="\r")
                
                random_suit = random.choice(["S","C","D","H",None])
                round_info = Tennis.PlayTennisRound(leaders[leader_index], dealers[dealer_index], random_suit)
                
                round_winner = round_info[1]
                
                outcomes[leader_index][dealer_index][round_winner] += 1
        

    
    print("Round Robin Tournament Results:")
    print()
    print(f"Each pairing consisted of {num_tournaments} games")
    print(f"Each leader played {len(dealers) * num_tournaments} games")
    print(f"Each dealer played {len(leaders) * num_tournaments} games")
    
    # Print leader stats
    print("\nLEADERS")
    leader_stats = []
    for leader_index in range(len(leaders)):
        hardest_opponent = None
        lowest_win_rate = 2
        total_win_rate = 0
        for dealer_index in range(len(dealers)):
            w = outcomes[leader_index][dealer_index][0]
            l = outcomes[leader_index][dealer_index][1]
            win_rate = w / (w + l)
            total_win_rate += win_rate
            
            if win_rate < lowest_win_rate:
                lowest_win_rate = win_rate
                hardest_opponent = dealers[dealer_index]
        leader_stats.append((leaders[leader_index].__name__,
            total_win_rate/len(dealers), hardest_opponent.__name__, lowest_win_rate))
    for leader_stat in sorted(leader_stats, key = lambda x: x[1], reverse = True):
        print(f"{leader_stat[0]}: {leader_stat[1]:.1%}")
        print(f"  Hardest opponent: {leader_stat[2]} ({leader_stat[3]:.1%})")
    
    # Print dealer stats
    print("\nDEALERS")
    dealer_stats = []
    for dealer_index in range(len(dealers)):
        hardest_opponent = None
        lowest_win_rate = 2
        total_win_rate = 0
        for leader_index in range(len(leaders)):
            w = outcomes[leader_index][dealer_index][1]
            l = outcomes[leader_index][dealer_index][0]
            win_rate = w / (w + l)
            total_win_rate += win_rate
            if win_rate < lowest_win_rate:
                lowest_win_rate = win_rate
                hardest_opponent = leaders[leader_index]
        dealer_stats.append((dealers[dealer_index].__name__,
            total_win_rate/len(leaders), hardest_opponent.__name__, lowest_win_rate))
    for leader_stat in sorted(dealer_stats, key = lambda x: x[1], reverse = True):
        print(f"{leader_stat[0]}: {leader_stat[1]:.1%}")
        print(f"  Hardest opponent: {leader_stat[2]} ({leader_stat[3]:.1%})")