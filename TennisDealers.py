import Tennis
import Deck
import random

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBidRandomDealer(Tennis.TennisPlayer):
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
class AgressiveDealer(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(3)

    def make_forehand_bid(self):
        return self.forehand.closest_bid_card(4)
    
    def play_forehand(self, trick_cards):
        self.forehand.sort_by_rank()
        return self.LowestWinningCard(trick_cards, self.forehand)
    
    def play_backhand(self, trick_cards):
        self.backhand.sort_by_rank()
        # if the forehand is winning, try to lose
        if Tennis.GetWinningCard(trick_cards, self.trump_suit) == trick_cards.cards[1]:
            return self.backhand.cards[-1] # play the lowest card
        else:
            return self.LowestWinningCard(trick_cards, self.backhand)
            
class PassiveDealer(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(0)

    def make_forehand_bid(self):
        return self.forehand.closest_bid_card(0)
    
    def play_forehand(self, trick_cards):
        return self.ThrowTrick(trick_cards)
        
    def play_backhand(self, trick_cards):
        return self.ThrowTrick(trick_cards)

# This is my (Dejvid) first attempt to make a 'smart' player
class MyFirstSmartDealer(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(0)

    def make_forehand_bid(self):
        return self.forehand.closest_bid_card(0)
    
    def play_forehand(self, trick_cards):
        self.forehand.sort_by_suit_and_rank()
        if self.forehand_wins < self.forehand_bid["value"]:
            firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first winning card
            if not firstWinningCard: # if no winning card can be found, play the lowest card
                firstWinningCard = self.forehand.cards[-1]
            return firstWinningCard
        else:
            firstLosingCard = Tennis.GetFirstLosingCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest card
                firstLosingCard = self.forehand.cards[0]
            return firstLosingCard
    
    def play_backhand(self, trick_cards):
        self.backhand.sort_by_suit_and_rank()
        # if the forehand is winning and needs to win, try to lose
        if (Tennis.GetWinningCard(trick_cards, self.trump_suit) == trick_cards.cards[1] and 
            self.forehand_wins < self.forehand_bid["value"]):
            return self.backhand.cards[-1] # play the lowest card
        else:
            # check if we met our goals
            if self.backhand_wins < self.backhand_bid["value"]:
                # try to win
                return self.HighestWinningCard(trick_cards, self.backhand)
            else:
                # try to lose
                return self.ThrowTrick(trick_cards)

# This is my (Dejvid) first attempt to make a 'smart' player
class MySecondSmartDealer(Tennis.TennisPlayer):
    def make_backhand_bid(self):
        return self.backhand.closest_bid_card(0)

    def make_forehand_bid(self):
        return self.forehand.closest_bid_card(0)
    
    def play_forehand(self, trick_cards):
        self.forehand.sort_by_suit_and_rank()
        if self.forehand_wins < self.forehand_bid["value"]:
            firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first winning card
            if not firstWinningCard: # if no winning card can be found, play the lowest card
                firstWinningCard = self.forehand.cards[-1]
            return firstWinningCard
        else:
            firstLosingCard = Tennis.GetFirstLosingCard(trick_cards, self.trump_suit, self.forehand.cards) # return the first losing card
            if not firstLosingCard: # if no losing card can be found, play the highest card
                firstLosingCard = self.forehand.cards[0]
            return firstLosingCard
    
    def play_backhand(self, trick_cards):
        self.backhand.sort_by_suit_and_rank()
        # if the forehand is winning and needs to win, try to lose
        if (Tennis.GetWinningCard(trick_cards, self.trump_suit) == trick_cards.cards[1] and 
            self.forehand_wins < self.forehand_bid["value"]):
            return self.backhand.cards[-1] # play the lowest card
        else:
            # check if we met our goals
            if self.backhand_wins < self.backhand_bid["value"]:
                # try to win
                return self.HighestWinningCard(trick_cards, self.backhand)
            else:
                # try to lose
                return self.ThrowTrick2(trick_cards)