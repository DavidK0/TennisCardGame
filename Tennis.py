from Deck import Deck
from Deck import Card
from TennisPlayers import TennisPlayer
from TennisPlayers import RandomTennisPlayer

def PlayTennisRound(player1: TennisPlayer, player2: TennisPlayer, trump_suit, verbose=False):
    players = [player1, player2]
    
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
    
    # Calculate errors and return them
    player_errors = []
    for player in players:
        forehand_errors = abs(player.forehand_bid_value - player.forehand_wins)
        backhand_errors = abs(player.backhand_bid_value - player.backhand_wins)
        total_errors = forehand_errors + backhand_errors
        player_errors.append(total_errors)
    return player_errors

if __name__ == "__main__":
    p1 = RandomTennisPlayer()
    p2 = RandomTennisPlayer()
    errors = PlayTennisRound(p1, p2, trump_suit=None, verbose=True)
    print(f"Errors: {errors}")
