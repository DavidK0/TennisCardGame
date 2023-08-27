# This script represents a deck of cards, and the cards

import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"
        
    def __eq__(self, other):
        if other == None:
            return False
        same_rank = self.rank == other.rank
        same_suit = self.suit == other.suit
        return same_rank and same_suit
    
    def numeric_rank(self):
        if self.rank == 'A':
            return 14
        elif self.rank == 'K':
            return 13
        elif self.rank == 'Q':
            return 12
        elif self.rank == 'J':
            return 11
        else:
            return int(self.rank)

class Deck:
    # creates an empty deck
    def __init__(self):
        self.cards = []
    
    # puts 52 cards in the deck and shuffles it
    def reset(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['C', 'S', 'H', 'D']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
    
    # shuffle the deck
    def shuffle(self):
        random.shuffle(self.cards)
    
    # checks if the given string represents a card in the deck
    # returns the card if it is in the deck, and None otherwise
    def has_card(self, card: Card):
        return card in self.cards
    
    # returns the given number of card of the top of the deck
    def draw(self, num):
        if num > len(self.cards):
            raise ValueError("Not enough cards in the deck.")
        return_deck = Deck()
        return_deck.cards = [self.cards.pop() for _ in range(num)]
        return return_deck
    
    # returns the given card, if it is in the deck
    def play(self, card: Card):
        if not isinstance(card,Card) or not self.has_card(card):
            raise Exception(f"Card '{card}' not found in the deck")
        self.cards.remove(card)
        return card
    
    # adds the given card or card to bottom of the deck
    def add(self, cards):
        if isinstance(cards, Card):
            self.cards.append(cards)
        elif isinstance(cards, list):
            self.cards.extend(cards)
        elif isinstance(cards, Deck):
            self.cards.extend(cards.cards)
    
    # returns the number of cards in the deck
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return f"[{', '.join([str(card) for card in self.cards])}]"

    # returns the card that is closest to the given rank
    # in the case of a tie, the lower cards by rank is chosen
    def closest_rank_card(self, rank):
        best_dist = 100 # some high value
        best_card = None
        for card in self.cards:
            new_dist = abs(rank - card.numeric_rank())
            if new_dist < best_dist or (new_dist == best_dist and card.numeric_rank() < rank):
                best_dist = new_dist
                best_card = card
        return best_card
        
    # returns the card that is closest to the given BID
    # in the case of a tie, the lower cards by rank is chosen
    # used for Tennis
    def closest_bid_card(self, bid):
        # the value of cards during a bid is different than during a trick
        def get_bid_value(card: Card):
            rank = card.numeric_rank()
            if rank == 13:
                return 0
            elif rank == 14:
                return 1
            else:
                return rank
        best_dist = 100 # some high value
        best_card = None
        for card in self.cards:
            new_dist = abs(bid - get_bid_value(card))
            if new_dist < best_dist or (new_dist == best_dist and get_bid_value(card) < bid):
                best_dist = new_dist
                best_card = card
        return best_card

    # sorts the deck so that the highest ranking cards are at the top
    # set reverse to false to put low ranking cards at the top
    def sort_by_rank(self, reverse=False):
        self.cards.sort(key=lambda card: -card.numeric_rank(), reverse=reverse)

    # sorts the deck so that the most common suit is on the top, and
    #   within a suit the highest rank is on the top
    def sort_by_suit_and_rank(self):
        suit_count = {'C': 0, 'D': 0, 'H': 0, 'S': 0}
        
        # Count the number of cards for each suit
        for card in self.cards:
            suit_count[card.suit] += 1
        
        # Sort the cards using a custom sorting key
        self.cards.sort(key=lambda card: (suit_count[card.suit], card.numeric_rank()), reverse=True)
    
    
    # find the average rank of this deck
    def average_numeric_rank(self):
        total_numeric_rank = 0
        for card in self.cards:
            total_numeric_rank += card.numeric_rank()
        return total_numeric_rank/len(self)

    # returns the count of the given suit
    def count_suit(self, suit):
        suit_count = 0
        for card in self.cards:
            if card.suit == suit:
                suit_count += 1
        return suit_count