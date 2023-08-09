from Deck import Deck
from Deck import Card
from TennisPlayers import TennisPlayer
from TennisPlayers import RandomTennisPlayer
from TennisPlayers import AverageBetRandomPlayer

def PlayTennisRound(player1: type, player2: type, trump_suit, verbose=False):
    players = [player1("leader"), player2("dealer")]
    
    deck = Deck() # create an empty deck
    deck.reset() # put 52 cards in and shuffle
    
    # deal 13 cards to each players hands
    for player in players:
        player.forehand = Deck()
        player.forehand.add(deck.draw(13))
        player.backhand = Deck()
        player.backhand.add(deck.draw(13))
    
    if verbose:
        print("Initial hands")
        print(f"Player 1 forehand: {players[0].forehand}")
        print(f"Player 1 backhand: {players[0].backhand}")
        print(f"Player 2 forehand: {players[1].forehand}")
        print(f"Player 2 backhand: {players[1].backhand}")
    
    # the value of cards during a bid is different than during a trick
    def get_bid_value(card: Card):
        rank = card.numeric_rank()
        if rank == 13:
            return 0
        elif rank == 14:
            return 1
        else:
            return rank
    
    # a handy function to wrap-up already revealed info
    def get_player_revealed_info(player: TennisPlayer):
        backhand_bid_card = player.backhand_bid_card
        forehand_bid_card = player.forehand_bid_card
        backhand_bid_value = player.backhand_bid_value
        forehand_bid_value = player.forehand_bid_value
        backhand_bid = {"card":backhand_bid_card, "value":backhand_bid_value}
        forehand_bid = {"card":forehand_bid_card, "value":forehand_bid_value}
        forehand_wins = player.forehand_wins
        backhand_wins = player.backhand_wins
        return (forehand_bid, backhand_bid, forehand_wins, backhand_wins)
    
    # make bids
    for player in players: # backhand bids
        card = player.make_backhand_bid() # get the bid card
        player.backhand_bid_card = player.backhand.play(card) # set the bid card
        player.backhand_bid_value = get_bid_value(player.backhand_bid_card) # set the bid value
    for i in range(2): # forehand bids
        opponent_revealed_info = get_player_revealed_info(players[1-i]) # get info about the opponent's bid
        card = players[i].make_forehand_bid(opponent_revealed_info) # get the bid card
        players[i].forehand_bid_card = players[i].forehand.play(card) # set the bid card
        players[i].forehand_bid_value = get_bid_value(players[i].forehand_bid_card) # set the bid value
    
    if verbose:
        print(f"Player 1 bids: {players[0].forehand_bid_value}, {players[0].backhand_bid_value}")
        print(f"Player 2 bids: {players[1].forehand_bid_value}, {players[1].backhand_bid_value}")
    
    # play 12 tricks
    for trick in range(12):
        trick_cards = Deck()
        
        # play four cards
        for i in range(4):
            player_index = i % 2
            opponent_revealed_info = get_player_revealed_info(players[1-player_index])
            
            # play one card
            card = players[player_index].play(trick_cards, opponent_revealed_info)
            # check if this is a forehand or backhand play
            if len(trick_cards)>1:
                players[player_index].forehand.play(card)
            else:
                players[player_index].backhand.play(card)
            trick_cards.add(card)
    
        # show the first play what was played on the last trick
        players[0].show(trick_cards)
        
        # determine the highest card
        lead_suit = trick_cards.cards[0].suit
        highest_rank = trick_cards.cards[0].numeric_rank()
        highest_card = trick_cards.cards[0]
        for card in trick_cards.cards[1:]:
            valid_suit = card.suit == trump_suit or card.suit == lead_suit
            if valid_suit and card.numeric_rank() >= highest_rank:
                highest_rank = card.numeric_rank()
                highest_card = card
        
        # give one win depending on the highest card
        if highest_card == trick_cards.cards[0]:
            players[0].forehand_wins += 1
        elif highest_card == trick_cards.cards[1]:
            players[1].forehand_wins += 1
        elif highest_card == trick_cards.cards[2]:
            players[0].backhand_wins += 1
        elif highest_card == trick_cards.cards[3]:
            players[1].backhand_wins += 1
        
        if verbose:
            print(f"Trick {trick}: {trick_cards} -> {str(highest_card)}")
    
    if verbose:
        print(f"P1 wins: {players[0].forehand_wins}, {players[0].backhand_wins}")
        print(f"P2 wins: {players[1].forehand_wins}, {players[1].backhand_wins}")
    
    ## Prepare information to be returned ##
    
    # Get bids, wins, and errors
    player_infos = []
    for i in range(2):
        player_bid_info = [players[i].forehand_bid_value, players[i].backhand_bid_value]
        player_win_info = [players[i].forehand_wins, players[i].backhand_wins]
        player_forehand_error = abs(players[i].forehand_bid_value - players[i].forehand_wins)
        player_backhand_error = abs(players[i].backhand_bid_value - players[i].backhand_wins)
        player_error_info = [player_forehand_error, player_backhand_error]
        player_infos.append((player_bid_info, player_win_info, player_error_info))

    # Find round winner
    p1_total_error = player_infos[0][2][0] + player_infos[0][2][1]
    p2_total_error = player_infos[1][2][0] + player_infos[1][2][1]
    if p1_total_error < p2_total_error:
        winner = 0
    elif p1_total_error > p2_total_error:
        winner = 1
    else:
        winner = -1

    round_info = (player_infos, winner)
    return round_info

# play two rounds, alternating dealer, with the given trump suit
def PlayTwoRounds(player1: type, player2: type, trump_suit):
    # trick one
    round1_info = PlayTennisRound(player1, player2, trump_suit=trump_suit, verbose=False)
    round2_info = PlayTennisRound(player2, player1, trump_suit=trump_suit, verbose=False)
    return round1_info, round2_info

# takes two lists of number, each with length 2, and adds them element wise
def add_number_pairs(number_pair1, number_pair2):
    return [number_pair1[0] + number_pair2[0], number_pair1[1] + number_pair2[1]]

if __name__ == "__main__":
    player1 = RandomTennisPlayer
    player2 = RandomTennisPlayer

    # the numer of pairs of rounds to play
    num_round_pairs = 100000

    # track stats
    p1_bids = [0, 0]
    p1_wins = [0, 0]
    p1_errors = [0, 0]

    p2_bids = [0, 0]
    p2_wins = [0, 0]
    p2_errors = [0, 0]

    leader_bids = [0, 0]
    leader_wins = [0, 0]
    leader_errors = [0, 0]

    dealer_bids = [0, 0]
    dealer_wins = [0, 0]
    dealer_errors = [0, 0]

    #for trump_suit in [None]:
    for round in range(num_round_pairs):
        print(f"Playing rounds: {round/num_round_pairs:.1%}", end="\r")
        trump_suit = None
        round1_info, round2_info = PlayTwoRounds(player1, player2, trump_suit)

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

            leader_bids = add_number_pairs(leader_bids, rounds[i][0][0][0])
            leader_wins = add_number_pairs(leader_wins, rounds[i][0][0][1])
            leader_errors = add_number_pairs(leader_errors, rounds[i][0][0][2])
            
            dealer_bids = add_number_pairs(dealer_bids, rounds[i][0][1][0])
            dealer_wins = add_number_pairs(dealer_wins, rounds[i][0][1][1])
            dealer_errors = add_number_pairs(dealer_errors, rounds[i][0][1][2])

    # print stats
    def nice_format(num_pair):
        return [f"{x / total_rounds:.2f}" for x in num_pair]

    total_rounds = num_round_pairs * 2
    print(f"average p1 bids: {nice_format(p1_bids)}")
    print(f"average p1 wins: {nice_format(p1_wins)}")
    print(f"average p1 errors: {nice_format(p1_errors)}")
    print()
    print(f"average p2 bids: {nice_format(p2_bids)}")
    print(f"average p2 wins: {nice_format(p2_wins)}")
    print(f"average p2 errors: {nice_format(p2_errors)}")
    print()
    print(f"average leader bids: {nice_format(leader_bids)}")
    print(f"average leader wins: {nice_format(leader_wins)}")
    print(f"average leader errors: {nice_format(leader_errors)}")
    print()
    print(f"average dealer bids: {nice_format(dealer_bids)}")
    print(f"average dealer wins: {nice_format(dealer_wins)}")
    print(f"average dealer errors: {nice_format(dealer_errors)}")