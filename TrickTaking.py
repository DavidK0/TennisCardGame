# This script handles tricks in trick taking games

from Deck import Deck
from Deck import Card

# This class represents one trick in trick taking cards games
class Trick():
    def __init__(self, trump_suit):
        self.cards = Deck() # all the cards in the trick
        
        self.trump_suit = trump_suit # a string or None
        self.lead_suit = None # the suit of the first card played
        
        self.winning_card = None # the winning card in the trick
        self.winning_index = None # the index of the winning card
    
    def __str__(self):
        cards_str = ",".join([str(card) for card in self.cards.cards])
        return f"[{self.trump_suit}] {cards_str} -> {str(self.winning_card)}"
        
    def __len__(self):
        return len(self.cards)
    
    def add_card(self, card):
        # Set lead suit
        if len(self.cards) == 0:
            self.lead_suit = card.suit
        
        # Check if this is a new winning card
        if self.would_win(card):
            self.winning_index = len(self.cards)
        
        self.cards.add(card) # add the card to the trick
        
        self.winning_card = self.cards[self.winning_index]
    
    # Returns true if the given card would win the trick
    def would_win(self, card):
        if len(self.cards) == 0:
            return True
        elif card.suit == self.winning_card.suit:
            if card.numeric_rank() > self.winning_card.numeric_rank():
                return True
        elif card.suit == self.trump_suit:
            return True
    
    # Returns a subset of a deck that includes only legal moves
    def get_legal_moves(self, deck):
        if len(self.cards) == 0:
            return deck.copy()
        elif self.lead_suit in [card.suit for card in deck.cards]:
            return_deck = Deck()
            return_deck.add([card for card in deck.cards if card.suit == self.lead_suit])
            return return_deck
        else:
            return deck.copy()
    
    # Returns the first card in the deck that would win this trick
    # Returns None if no such card can be found
    def first_winning_card(self, deck):
        for card in cards:
            if self.would_win(card):
                return card
        return None
    
    # Returns the first card in the deck that would lose this trick
    # Returns None if no such card can be found
    def first_lossing_card(self, deck):
        for card in cards:
            if not self.would_win(card):
                return card
        return None