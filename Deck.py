import random

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"
        
    def __eq__(self, other):
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
            return self.rank

class Deck:
    # creates an empty deck
    def __init__(self):
        self.cards = []
    
    # puts 52 cards in the deck and shuffles it
    def reset(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['C', 'D', 'H', 'S']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.shuffle()
    
    # shuffle the deck
    def shuffle(self, num):
        random.shuffle(self.cards)
    
    # checks if the given string represents a card in the deck
    # returns the card if it is in the deck, and None otherwise
    def has_card(self, card_str: str):
        if card_str in [str(card) for card in self.cards]:
            card = next(card_obj for card_obj in self.cards if str(card_obj) == card)
        else:
            card = None
        return card
    
    # returns the given number of card of the top of the deck
    def draw(self, num):
        if num > len(self.cards):
            raise ValueError("Not enough cards in the deck.")
        return [self.cards.pop() for _ in range(num)]
    
    # returns the given card, if it is in the deck
    def play(self, card: Card):
        assert(self.has_card(str(card)))
        self.cards.remove(card)
        return card
    
    # adds the given card to bottom of the deck
    def add(self, card):
        self.cards.append(card)

