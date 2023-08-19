import Tennis
import Deck
import random

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBidRandomLeader(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(1)
    
    def make_forehand_bid(self):
        if self.role == "leader":
            return self.forehand.closest_bid_card(7)
        else:
            return self.forehand.closest_bid_card(1)
    
    def play_forehand(self, trick_cards):
        return random.choice(self.forehand.cards)
        
    def play_backhand(self, trick_cards):
        return random.choice(self.backhand.cards)


# This Tennis player trys to agressively win every trick.
class AgressiveLeader(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(1)

    def make_forehand_bid(self):
        return self.forehand.closest_bid_card(9)
    
    def play_forehand(self, trick_cards):
        return random.choice(self.forehand.cards)
    
    def play_backhand(self, trick_cards):
        self.backhand.sort_by_rank()
        # if the forehand is winning, try to lose
        # otherwise try to win
        if Tennis.GetWinningCard(trick_cards, self.trump_suit) == trick_cards.cards[0]:
            return self.backhand.cards[-1] # play the lowest card
        else:
            return self.LowestWinningCard(trick_cards, self.trump_suit, self.backhand)

# This is my (Dejvid) first attempt to make a 'smart' player
class MyFirstSmartLeader(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        average_rank = self.backhand.average_numeric_rank()
        target_bid = average_rank - 6
        return self.backhand.closest_bid_card(target_bid)

    def make_forehand_bid(self):
        average_rank = self.forehand.average_numeric_rank()
        target_bid = average_rank - 2.3
        return self.forehand.closest_bid_card(target_bid)
    
    def play_forehand(self, trick_cards):
        self.backhand.sort_by_rank()
        # check if we met our goals
        if self.forehand_wins < self.forehand_bid["value"]:
            return self.forehand.cards[0] # play the highest card
        else:
            return self.forehand.cards[-1] # play the lowest card
    
    def play_backhand(self, trick_cards):
        self.backhand.sort_by_rank()
        # if the forehand is winning, try to lose
        if Tennis.GetWinningCard(trick_cards, self.trump_suit) == trick_cards.cards[0]:
            return self.backhand.cards[-1] # play the lowest card
        else:
            # check if we met our goals
            if self.backhand_wins < self.backhand_bid["value"]:
                # try to win
                return self.HighestWinningCard(trick_cards, self.trump_suit, self.backhand)
            else:
                # try to lose
                return self.ThrowTrick(trick_cards, self.trump_suit)