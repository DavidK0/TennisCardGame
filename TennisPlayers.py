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
    def make_backhand_bid(self):
        raise NotImplementedError("Subclasses must implement the make_backhand_bid method")
    
    # Returns a card from the forehand
    def make_forehand_bid(self, opponent_revealed_info):
        raise NotImplementedError("Subclasses must implement the make_forehand_bid method")
        
    # Returns a card
    # the current hand (fore or back) must be found implicitly
    def play(self, trick_cards, opponent_revealed_info):
        if len(trick_cards)>1: # return a forehand card
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
    def make_backhand_bid(self):
        return random.choice(self.backhand.cards)
    
    def make_forehand_bid(self, opponent_revealed_info):
        return random.choice(self.forehand.cards)
    
    def play(self, trick_card, opponent_revealed_info):
        if len(trick_card)>1: # return a forehand card
            return random.choice(self.forehand.cards)
        else: # return a backhand card
            return random.choice(self.backhand.cards)

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBetRandomPlayer(TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_rank_card(1)
    
    def make_forehand_bid(self, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_rank_card(8)
        else:
            return self.forehand.closest_rank_card(1)
    
    def play(self, trick_card, opponent_revealed_info):
        if len(trick_card)>1: # return a forehand card
            return random.choice(self.forehand.cards)
        else: # return a backhand card
            return random.choice(self.backhand.cards)