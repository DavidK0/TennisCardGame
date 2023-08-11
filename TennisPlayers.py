from Deck import Deck

# This class is the base class for Tennis players.
#
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

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBidRandomPlayer(TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        return self.backhand.closest_rank_card(0)
    
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_rank_card(8)
        else:
            return self.forehand.closest_rank_card(0)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if len(trick_cards)<2: # return a forehand card
            return random.choice(self.forehand.cards)
        else: # return a backhand card
            return random.choice(self.backhand.cards)

# This Tennis player trys to agressively win every trick.
class AgressivePlayer(TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        if self.role == "leader":
            return self.backhand.closest_rank_card(4)
        else:
            return self.backhand.closest_rank_card(4)

    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_rank_card(6)
        else:
            return self.forehand.closest_rank_card(3)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        import Tennis
        self.forehand.sort_by_rank(False)
        self.backhand.sort_by_rank(False)
        if self.role == "leader":
            if len(trick_cards)<2: # return a forehand card
                firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.forehand.cards) # return the first winning card
                if not firstWinningCard: # if no winning card can be found, play something random
                    firstWinningCard = self.forehand.cards[0]
                return firstWinningCard

            else: # return a backhand card
                firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                if not firstWinningCard: # if no winning card can be found, play something random
                    firstWinningCard = random.choice(self.backhand.cards)
                return firstWinningCard
        else:
            if len(trick_cards)<2: # return a forehand card
                firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.forehand.cards) # return the first winning card
                if not firstWinningCard: # if no winning card can be found, play something random
                    firstWinningCard = random.choice(self.forehand.cards)
                return firstWinningCard

            else: # return a backhand card
                firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                if not firstWinningCard: # if no winning card can be found, play something random
                    firstWinningCard = random.choice(self.backhand.cards)
                return firstWinningCard