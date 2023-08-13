import Tennis
import random

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBidRandomPlayer(Tennis.TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        return self.backhand.closest_bid_card(1)
    
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_bid_card(8)
        else:
            return self.forehand.closest_bid_card(1)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if len(trick_cards)<2: # return a forehand card
            return random.choice(self.forehand.cards)
        else: # return a backhand card
            return random.choice(self.backhand.cards)

# This Tennis player trys to agressively win every trick.
class AgressivePlayer(Tennis.TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        if self.role == "leader":
            return self.backhand.closest_bid_card(1)
        else:
            return self.backhand.closest_bid_card(2)

    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_bid_card(9)
        else:
            return self.forehand.closest_bid_card(5)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        self.backhand.sort_by_rank()
        self.forehand.sort_by_rank()
        if self.role == "leader":
            if len(trick_cards)<2: # return a forehand card
                return self.forehand.cards[0] # play the highest card
            else: # return a backhand card
                # if the forehand is winning, try to lose
                if Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[0]:
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                    if not firstWinningCard: # if no winning card can be found, play the lowest card
                        firstWinningCard = self.backhand.cards[-1]
                    return firstWinningCard
        else:
            if len(trick_cards)<2: # return a forehand card
                firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.forehand.cards) # return the first winning card
                if not firstWinningCard: # if no winning card can be found, play the lowest card
                    firstWinningCard = self.forehand.cards[-1]
                return firstWinningCard
            else: # return a backhand card
                # if the forehand is winning, try to lose
                if Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[1]:
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                    if not firstWinningCard: # if no winning card can be found, play the lowest card
                        firstWinningCard = self.backhand.cards[-1]
                    return firstWinningCard
                    
# This Tennis player trys to agressively win every trick as the leader and lose every trick
#   as the dealer
class AgressiveLeaderPassiveDealerPlayer(Tennis.TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        if self.role == "leader":
            return self.backhand.closest_bid_card(2)
        else:
            return self.backhand.closest_bid_card(0)

    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_bid_card(9)
        else:
            return self.forehand.closest_bid_card(0)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            self.backhand.sort_by_rank()
            self.forehand.sort_by_rank()
            if len(trick_cards)<2: # return a forehand card
                return self.forehand.cards[0] # play the highest card
            else: # return a backhand card
                # if the forehand is winning, try to lose
                if Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[0]:
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    firstWinningCard = Tennis.GetFirstWinningCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                    if not firstWinningCard: # if no winning card can be found, play the lowest card
                        firstWinningCard = self.backhand.cards[-1]
                    return firstWinningCard
        else:
            self.backhand.sort_by_suit_and_rank()
            self.forehand.sort_by_suit_and_rank()
            if len(trick_cards)<2: # return a forehand card
                firstLosingCard = Tennis.GetFirstLosingCard(trick_cards, trump_suit, self.forehand.cards) # return the first winning card
                if not firstLosingCard: # if no winning card can be found, play the highest card
                    firstLosingCard = self.forehand.cards[-1]
                return firstLosingCard
            else: # return a backhand card
                firstLosingCard = Tennis.GetFirstLosingCard(trick_cards, trump_suit, self.backhand.cards) # return the first winning card
                if not firstLosingCard: # if no winning card can be found, play the highest card
                    firstLosingCard = self.backhand.cards[-1]
                return firstLosingCard