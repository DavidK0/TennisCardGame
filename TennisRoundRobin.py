# This script runs a round robin tournament

import random

import Tennis
from Tennis import RandomTennisPlayer
from TennisPlayers import AverageBidRandomPlayer
from TennisPlayers import AgressivePlayer
from TennisPlayers import AgressiveLeaderPassiveDealerPlayer

# Plays a round robin tournament with all players and tracks their wins
def PlayRoundRobinTournament(players):
    wins = [0] * len(players)

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            random_suit = random.choice(["S","C","D","H",None])
            round_info = Tennis.PlayTwoRounds(players[i], players[j], random_suit)
            
            r1 = round_info[0][1] # round 1 winner
            r2 = round_info[1][1] # round 2 winner
            
            if r1 == 0:
                wins[i] += .5
            elif r1 == 1:
                wins[j] += .5
            else:
                wins[i] += .25
                wins[j] += .25
                
            if r2 == 0:
                wins[j] += .5
            elif r2 == 1:
                wins[i] += .5
            else:
                wins[j] += .25
                wins[i] += .25

    return wins

if __name__ == "__main__":
    # List of players participating in the round-robin tournament
    players = [RandomTennisPlayer, AverageBidRandomPlayer, AgressivePlayer, AgressiveLeaderPassiveDealerPlayer]  # Add more players here if needed
    
    total_players = len(players)
    player_names = [player.__name__ for player in players]
    num_tournaments = 1000

    wins = [0] * len(players)
    for i in range(num_tournaments):
        wins = [sum(x) for x in zip(wins, PlayRoundRobinTournament(players))]
        
        progress = (i + 1) / num_tournaments
        print(f"Progress: {progress:.1%}", end="\r")
    
    print("Round Robin Tournament Results:")
    print(f"Each player played {(total_players - 1) * num_tournaments} games")

    # Create a list of tuples containing player names and their corresponding wins
    results = [(player_names[i], wins[i]) for i in range(total_players)]

    # Sort the results based on wins in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    for i, (player_name, player_wins) in enumerate(results):
        win_percentage = player_wins / ((total_players - 1) * num_tournaments)  # -1 to exclude self-match
        print(f"{i+1}. {player_name}: {player_wins} wins ({win_percentage:.1%})")