# This is an implementation of Tennis (https://etgdesign.com/games/tennis/)

from Deck import Deck
from Deck import Card
import copy

# play one tennis round
# player1 will be the leader, player2 is the dealer
# trump_suit is one of the suits in Deck.py
def PlayTennisRound(leader: type, dealer: type, trump_suit, verbose=False):
    # Initiate both players
    leader = leader("leader", trump_suit)
    dealer = dealer("dealer", trump_suit)
    
    # Keep a record of all the moves made
    # The record is simply a list of 52 cards in the order they were played
    game_record = []
    
    deck = Deck() # create an empty deck
    deck.reset() # put 52 cards in
    deck.shuffle() # shuffle the deck
    
    # Deal 13 cards to each player's backhand
    for player in [leader, dealer]:
        player.backhand = Deck()
        player.backhand.add(deck.draw(13))
        for card in player.backhand.cards:
            player.opponent_both_hands.play(card)
    
    # Print the backhands
    if verbose:
        print(f"Trump suit: {trump_suit}".ljust(30))
        print(f"Player 1 backhand: {leader.backhand}")
        print(f"Player 2 backhand: {dealer.backhand}")
    
    # the value of cards during a bid is different than during a trick
    def get_bid_value(card: Card):
        rank = card.numeric_rank()
        if rank == 13:
            return 0
        elif rank == 14:
            return 1
        else:
            return rank
    
    # Place backhand bids
    for player in [leader, dealer]:
        card = player.make_backhand_bid() # get the bid card
        
        player.backhand_bid["card"] = player.backhand.play(card) # set the bid card
        player.backhand_bid["value"] = get_bid_value(player.backhand_bid["card"]) # set the bid value
        
        game_record.append(card) # Update the game record
    
    # Revealed the backhand bids
    leader.opponent_both_hands.play(dealer.backhand_bid["card"])
    dealer.opponent_both_hands.play(leader.backhand_bid["card"])
    for player in [leader, dealer]:
        player.reveal_backhand_bids(leader.backhand_bid, dealer.backhand_bid)
    
    # Deal 13 cards to each player's forehand
    for player in [leader, dealer]:
        player.forehand = Deck()
        player.forehand.add(deck.draw(13))
        for card in player.forehand.cards:
            player.opponent_both_hands.play(card)
    
    # Place forehand bids
    for player in [leader, dealer]:
        card = player.make_forehand_bid() # get the bid card
        player.forehand_bid["card"] = player.forehand.play(card) # set the bid card
        player.forehand_bid["value"] = get_bid_value(player.forehand_bid["card"]) # set the bid value
        game_record.append(card) # Update the game record
    
    # Revealed the forehand bids
    leader.opponent_both_hands.play(dealer.forehand_bid["card"])
    dealer.opponent_both_hands.play(leader.forehand_bid["card"])
    for player in [leader, dealer]:
        player.reveal_forehand_bids(leader.forehand_bid, dealer.forehand_bid)
    
    if verbose:
        print(f"Player 1 forehand: {leader.forehand}")
        print(f"Player 2 forehand: {dealer.forehand}")
        print(f"Player 1 bids: [{leader.forehand_bid['card']}, {leader.backhand_bid['card']}]")
        print(f"Player 2 bids: [{dealer.forehand_bid['card']}, {dealer.backhand_bid['card']}]")
    
    # Play 12 tricks
    for trick in range(1, 13):
        trick_cards = Deck()
        
        # Play four cards
        # Each time a card is played four actions happen
        # The card is removed from the players hand, the opponent is informed,
        #   trick_cards is updated, and the game_record is update
        
        played_card = leader.forehand.play(leader.play_forehand(trick_cards))
        dealer.opponent_both_hands.play(played_card)
        trick_cards.add(played_card)
        game_record.append(played_card)
        
        played_card = dealer.forehand.play(dealer.play_forehand(trick_cards))
        leader.opponent_both_hands.play(played_card)
        trick_cards.add(played_card)
        game_record.append(played_card)
        
        played_card = leader.backhand.play(leader.play_backhand(trick_cards))
        dealer.opponent_both_hands.play(played_card)
        trick_cards.add(played_card)
        game_record.append(played_card)
        
        played_card = dealer.backhand.play(dealer.play_backhand(trick_cards))
        trick_cards.add(played_card)
        leader.opponent_both_hands.play(played_card)
        game_record.append(played_card)
        
        # determine the highest card
        highest_card = GetWinningCard(trick_cards, trump_suit)
        
        # give one win depending on the highest card
        if highest_card == trick_cards.cards[0]:
            leader.forehand_wins += 1
            dealer.opponent_forehand_wins+= 1
        elif highest_card == trick_cards.cards[1]:
            dealer.forehand_wins += 1
            leader.opponent_forehand_wins += 1
        elif highest_card == trick_cards.cards[2]:
            leader.backhand_wins += 1
            dealer.opponent_backhand_wins += 1
        elif highest_card == trick_cards.cards[3]:
            dealer.backhand_wins += 1
            leader.opponent_backhand_wins += 1
        
        if verbose:
            print(f"Trick {trick}: {trick_cards} -> {str(highest_card)}")
    
    ## Prepare information to be returned ##
    
    # Get bids, wins, and errors
    player_infos = []
    for player in [leader, dealer]:
        player_bid_info = [player.forehand_bid["value"], player.backhand_bid["value"]]
        player_win_info = [player.forehand_wins, player.backhand_wins]
        player_forehand_error = abs(player.forehand_bid["value"] - player.forehand_wins)
        player_backhand_error = abs(player.backhand_bid["value"] - player.backhand_wins)
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
            
    if verbose:
        print(f"Leader score: [{leader.forehand_bid['value']}, {leader.backhand_bid['value']}] - [{leader.forehand_wins}, {leader.backhand_wins}] = [{player_infos[0][2][0]}, {player_infos[0][2][1]}] -> {p1_total_error}  {type(leader).__name__}")
        print(f"Dealer score: [{dealer.forehand_bid['value']}, {dealer.backhand_bid['value']}] - [{dealer.forehand_wins}, {dealer.backhand_wins}] = [{player_infos[1][2][0]}, {player_infos[1][2][1]}] -> {p2_total_error}  {type(dealer).__name__}")
        print()

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

# Takes a list of game records and prints a bunch of stats about the game
def get_game_stats(game_records: list):
    pass

# This class is the base class for Tennis players.
class TennisPlayer:
    def __init__(self, role, trump_suit):
        # None of these value should ever be set by the manually
        
        self.trump_suit = trump_suit
        
        # Information about this player #
        
        self.role = role # 'leader' or 'dealer'
        
        # One deck for each hand
        self.forehand = Deck()
        self.backhand = Deck()
        
        # One dict (keys = 'card', 'value') for each hand
        # The data types for 'card' and 'value' are Card and int respectively
        self.forehand_bid = {"card": None, "value": None}
        self.backhand_bid = {"card": None, "value": None}
        
        # One int for each hand
        self.forehand_wins = 0
        self.backhand_wins = 0
        
        # Information about the opponent #
        
        # One dict for the all the cards the opponent has
        self.opponent_both_hands = Deck()
        self.opponent_both_hands.reset()
        
        # One dict (keys = 'card', 'value') for each hand
        self.opponent_forehand_bid = None
        self.opponent_backhand_bid = None
        
        # One int for each hand
        self.opponent_forehand_wins = 0
        self.opponent_backhand_wins = 0
        
    # Returns a card from the backhand
    def make_backhand_bid(self):
        raise NotImplementedError("Subclasses must implement the make_backhand_bid method")
    
    # Returns a card from the forehand
    def make_forehand_bid(self):
        raise NotImplementedError("Subclasses must implement the make_forehand_bid method")
    
    # Reveal the forehand bids
    def reveal_forehand_bids(self, leader_forehand_bid, dealer_forehand_bid):
        if self.role == "leader":
            self.forehand_bid = leader_forehand_bid
            self.opponent_forehand_bid = dealer_forehand_bid
        else:
            self.forehand_bid = dealer_forehand_bid
            self.opponent_forehand_bid = leader_forehand_bid
    
    # Reveal the backhand bids
    def reveal_backhand_bids(self, leader_backhand_bid, dealer_backhand_bid):
        if self.role == "leader":
            self.backhand_bid = leader_backhand_bid
            self.opponent_backhand_bid = dealer_backhand_bid
        else:
            self.backhand_bid = dealer_backhand_bid
            self.opponent_backhand_bid = leader_backhand_bid
            
        
    # Returns a card
    def play_forehand(self, trick_cards):
        raise NotImplementedError("Subclasses must implement the play_forehand method")
        
    # Returns a card
    def play_backhand(self, trick_cards):
        raise NotImplementedError("Subclasses must implement the play_backhand method")

    def LowestWinningCard(self, trick_cards, deck):
        deck.sort_by_rank(True)
        firstWinningCard = GetFirstWinningCard(trick_cards, self.trump_suit, deck.cards) # return the first winning card
        if not firstWinningCard: # if no winning card can be found, play the lowest card
            firstWinningCard = deck.cards[0]
        return firstWinningCard

    def HighestWinningCard(self, trick_cards, deck):
        deck.sort_by_rank()
        firstWinningCard = GetFirstWinningCard(trick_cards, self.trump_suit, deck.cards) # return the first winning card
        if not firstWinningCard: # if no winning card can be found, play the highest card
            firstWinningCard = deck.cards[0]
        return firstWinningCard
    
    # Attempt to lose this trick by mismatching suits
    # If losing is impossible, play the highest card
    def ThrowTrick(self, trick_cards):
        self.backhand.sort_by_suit_and_rank()
        self.forehand.sort_by_suit_and_rank()
        if len(trick_cards)<2: # return a forehand card
            firstLosingCard = GetFirstLosingCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest card
                firstLosingCard = self.forehand.cards[0]
            return firstLosingCard
        else: # return a backhand card
            firstLosingCard = GetFirstLosingCard(trick_cards, self.trump_suit, self.backhand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest card
                firstLosingCard = self.backhand.cards[0]
            return firstLosingCard

    # Attempt to lose this trick by mismatching suits, in a special way
    # If losing is impossible, play the highest card
    def ThrowTrick2(self, trick_cards):
        suit_count = {'C': self.opponent_both_hands.count_suit("C"),
                        'D': self.opponent_both_hands.count_suit("D"),
                        'H': self.opponent_both_hands.count_suit("H"),
                        'S': self.opponent_both_hands.count_suit("S")}
        my_forehand_suit_count = {'C': self.forehand.count_suit("C"),
                                  'D': self.forehand.count_suit("D"),
                                  'H': self.forehand.count_suit("H"),
                                  'S': self.forehand.count_suit("S")}
        my_backhand_suit_count = {'C': self.forehand.count_suit("C"),
                                  'D': self.forehand.count_suit("D"),
                                  'H': self.forehand.count_suit("H"),
                                  'S': self.forehand.count_suit("S")}
        

        sorted_suits = sorted(suit_count.keys(), key=lambda suit: suit_count[suit], reverse=True)
        my_forehand_sorted_suits = sorted(my_forehand_suit_count.keys(), key=lambda suit: my_forehand_suit_count[suit], reverse=True)
        my_backhand_sorted_suits = sorted(my_backhand_suit_count.keys(), key=lambda suit: my_backhand_suit_count[suit], reverse=True)

        # Sort the cards using a custom sorting key
        self.forehand.cards = sorted(self.forehand.cards, key=lambda card: (sorted_suits.index(card.suit),my_forehand_sorted_suits.index(card.suit), card.numeric_rank()), reverse=True)
        self.backhand.cards = sorted(self.backhand.cards, key=lambda card: (sorted_suits.index(card.suit),my_backhand_sorted_suits.index(card.suit), card.numeric_rank()), reverse=True)
        
        #self.backhand.sort_by_suit_and_rank()
        #self.forehand.sort_by_suit_and_rank()
        if len(trick_cards)<2: # return a forehand card
            firstLosingCard = GetFirstLosingCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest common card
                firstLosingCard = self.forehand.cards[0]
            return firstLosingCard
        else: # return a backhand card
            firstLosingCard = GetFirstLosingCard(trick_cards, self.trump_suit, self.backhand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest common  card
                firstLosingCard = self.backhand.cards[0]
            return firstLosingCard
    
    # Returns True if card1 beats card2
    # card2 can only beat card1 if card2 matches suit with card1 or with trump_suit
    def CompareCards(self, card1, card2):
        if card1.suit == card2.suit or card2.suit == self.trump_suit:
            return card1.numeric_rank() > card2.numeric_rank()
        else:
            return True
        

# This Tennis player always picks a random card
import random
class RandomTennisPlayer(TennisPlayer):
    def make_backhand_bid(self):
        return random.choice(self.backhand.cards)
    
    def make_forehand_bid(self):
        return random.choice(self.forehand.cards)
    
    def play_backhand(self, trick_cards):
        return random.choice(self.backhand.cards)
        
    def play_forehand(self, trick_cards):
        return random.choice(self.forehand.cards)

# This Tennis player can be used to let a human play via the command line
import re, os
class HumanCommandLinePlayer(TennisPlayer):
    def validate_playing_card(self,input_str):
        pattern = r'^([2-9]|10|[JQKA])([CDHS])$'
        match = re.match(pattern, input_str)
        if match:
            rank, suit = match.groups()
            return rank, suit
        else:
            return None, None
    
    def make_backhand_bid(self, trump_suit):
        os.system('cls')
        print(f"You are playing as the {self.role}")
        print(f"Your backhand: {self.backhand}")
        print(f"Trump suit: {trump_suit}")
        card = None
        while not self.backhand.has_card(card):
            card_str = input("Enter a card for your backhand bid: ").upper()
            rank, suit = self.validate_playing_card(card_str)
            if rank and suit:
                card = Card(rank, suit)
        return card
    
    # doesn't work
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        os.system('cls')
        print(f"You are playing as the {self.role}")
        print(f"\nYour forehand: {self.forehand}")
        print(f"Your backhand: {self.backhand}")
        print()
        print(f"Your backhand bid: {self.backhand_bid_card}")
        print(f"Opponent's backhand bid: {opponent_revealed_info[1]['card']}")
        print()
        print(f"Trump suit: {trump_suit}")
        card = None
        while not self.forehand.has_card(card):
            card_str = input("Enter a card for your forehand bid: ").upper()
            rank, suit = self.validate_playing_card(card_str)
            if rank and suit:
                card = Card(rank, suit)
        return card
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        os.system('cls')
        print(f"You are playing as the {self.role}")
        print(f"\nYour forehand: {self.forehand}")
        print(f"Your backhand: {self.backhand}")
        print()
        print(f"Your bids: {self.forehand_bid_card}, {self.backhand_bid_card}")
        print(f"Opponent's bids: {opponent_revealed_info[0]['card']}, {opponent_revealed_info[1]['card']}")
        print()
        print(f"Trump suit: {trump_suit}")
        print(f"Trick: {trick_cards}")
        card = None
        if len(trick_cards)<2: # return a forehand card
            while not self.forehand.has_card(card):
                card_str = input("Play a card form your forehand: ").upper()
                rank, suit = self.validate_playing_card(card_str)
                if rank and suit:
                    card = Card(rank, suit)
            return card
        else: # return a backhand card
            while not self.backhand.has_card(card):
                card_str = input("Play a card form your backhand: ").upper()
                rank, suit = self.validate_playing_card(card_str)
                if rank and suit:
                    card = Card(rank, suit)
            return card
    
    def show(self, trick_cards):
        os.system('cls')
        print(f"The last card played was the {trick_cards.cards[-1]}")
        input("Enter anything to continue")