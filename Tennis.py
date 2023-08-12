# This is an implementation of Tennis (https://etgdesign.com/games/tennis/)

from Deck import Deck
from Deck import Card

# play one tennis round
# player1 will be the leader, player2 is the dealer
# trump_suit is one of the suits in Deck.py
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
        card = player.make_backhand_bid(trump_suit) # get the bid card
        player.backhand_bid_card = player.backhand.play(card) # set the bid card
        player.backhand_bid_value = get_bid_value(player.backhand_bid_card) # set the bid value
    for i in range(2): # forehand bids
        opponent_revealed_info = get_player_revealed_info(players[1-i]) # get info about the opponent's bid
        card = players[i].make_forehand_bid(trump_suit, opponent_revealed_info) # get the bid card
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
            card = players[player_index].play(trick_cards, trump_suit, opponent_revealed_info)
            # check if this is a forehand or backhand play
            if len(trick_cards)<2:
                players[player_index].forehand.play(card)
            else:
                players[player_index].backhand.play(card)
            trick_cards.add(card)

        # show the first play what was played on the last trick
        players[0].show(trick_cards)
        
        # determine the highest card
        highest_card = GetWinningCard(trick_cards, trump_suit)
        
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
        print()
    
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

# returns the winning card from this trick
def GetWinningCard(trick_cards, trump_suit):
    if len(trick_cards) == 0:
        return None
    
    lead_suit = trick_cards.cards[0].suit
    highest_rank = trick_cards.cards[0].numeric_rank()
    highest_card = trick_cards.cards[0]
    for card in trick_cards.cards[1:]:
        valid_suit = card.suit == trump_suit or card.suit == lead_suit
        if not valid_suit:
            continue
        if ((highest_card.suit == trump_suit and card.numeric_rank() > highest_rank) or
            (highest_card.suit == lead_suit and card.numeric_rank() >= highest_rank)):
            highest_rank = card.numeric_rank()
            highest_card = card
    return highest_card

# play two rounds, alternating dealer, with the given trump suit
def PlayTwoRounds(player1: type, player2: type, trump_suit, verbose=False):
    round1_info = PlayTennisRound(player1, player2, trump_suit, verbose)
    round2_info = PlayTennisRound(player2, player1, trump_suit, verbose)
    return round1_info, round2_info
    
    from Deck import Deck

# looks through the list of cards and returns the first card that would win this trick
# returns None if no winning card is found
def GetFirstWinningCard(trick_cards, trump_suit, cards: list):
    for card in cards:
        new_trick = Deck()
        new_trick.cards = [x for x in trick_cards.cards]
        new_trick.add(card)
        if GetWinningCard(new_trick, trump_suit) == card:
            return card
    return None
    
# looks through the list of cards and returns the first card that would not win this trick
# returns None if no losing card is found
def GetFirstLosingCard(trick_cards, trump_suit, cards: list):
    for card in cards:
        new_trick = Deck()
        new_trick.cards = [x for x in trick_cards.cards]
        new_trick.add(card)
        if GetWinningCard(new_trick, trump_suit) != card:
            return card
    return None

# This class is the base class for Tennis players.
#
# opponent_revealed_info is a argument passsed to two functions. It is a tuple containing four elements:
#   forehand_bid: a dictionary with keys "card" and "value"
#   backhand_bid: a dictionary with keys "card" and "value"
#   forehand_wins: an int
#   backhand_wins: an int
class TennisPlayer:
    def __init__(self, role):
        # None of these value should ever be set by the player
        self.role = role
        self.forehand = None
        self.backhand = None
        self.forehand_bid_card = None
        self.forehand_bid_value = None
        self.backhand_bid_card = None
        self.backhand_bid_value = None
        self.forehand_wins = 0
        self.backhand_wins = 0
    
    # Returns a card from the backhand
    def make_backhand_bid(self, trump_suit):
        raise NotImplementedError("Subclasses must implement the make_backhand_bid method")
    
    # Returns a card from the forehand
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        raise NotImplementedError("Subclasses must implement the make_forehand_bid method")
        
    # Returns a card
    # the current hand (fore or back) must be found implicitly
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if len(trick_cards)<2: # return a forehand card
            pass
        else: # return a backhand card
            pass
        raise NotImplementedError("Subclasses must implement the play method")
    
    # this is optionally used by the leader to see the last card played in a trick
    def show(self, trick_cards):
        pass

# This Tennis player always picks a random card
import random
class RandomTennisPlayer(TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        return random.choice(self.backhand.cards)
    
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        return random.choice(self.forehand.cards)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if len(trick_cards)<2: # return a forehand card
            return random.choice(self.forehand.cards)
        else: # return a backhand card
            return random.choice(self.backhand.cards)