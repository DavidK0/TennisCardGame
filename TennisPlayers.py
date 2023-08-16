import Tennis
import random

# This Tennis player makes a specific bid but otherwise plays randomly
# The bid is the average win in a Random vs. Random faceoff
class AverageBidRandomPlayer(Tennis.TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        return self.backhand.closest_bid_card(1)
    
    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_bid_card(7)
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
            return self.backhand.closest_bid_card(3)

    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            return self.forehand.closest_bid_card(9)
        else:
            return self.forehand.closest_bid_card(4)
    
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
                    return self.LowestWinningCard(trick_cards, trump_suit, self.backhand)
        else:
            if len(trick_cards)<2: # return a forehand card
                return self.LowestWinningCard(trick_cards, trump_suit, self.forehand)
            else: # return a backhand card
                # if the forehand is winning, try to lose
                if Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[1]:
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    return self.LowestWinningCard(trick_cards, trump_suit, self.backhand)
                    
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
                    return self.LowestWinningCard(trick_cards, trump_suit, self.backhand)
        else:
            return self.ThrowTrick(trick_cards, trump_suit)

# This is my (Dejvid) first attempt to make a 'smart' player
class MyFirstSmartTennisPlayer(Tennis.TennisPlayer):
    def make_backhand_bid(self, trump_suit):
        if self.role == "leader":
            average_rank = self.backhand.average_numeric_rank()
            target_bid = average_rank - 6
            return self.backhand.closest_bid_card(target_bid)
        else:
            return self.backhand.closest_bid_card(0)

    def make_forehand_bid(self, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            average_rank = self.forehand.average_numeric_rank()
            target_bid = average_rank - 2.3
            return self.forehand.closest_bid_card(target_bid)
        else:
            return self.forehand.closest_bid_card(0)
    
    def play(self, trick_cards, trump_suit, opponent_revealed_info):
        if self.role == "leader":
            self.backhand.sort_by_rank()
            self.forehand.sort_by_rank()
            if len(trick_cards)<2: # return a forehand card
                # check if we met our goals
                if self.forehand_wins < self.forehand_bid_value:
                    return self.forehand.cards[0] # play the highest card
                else:
                    return self.forehand.cards[-1] # play the lowest card
            else: # return a backhand card
                # if the forehand is winning, try to lose
                if Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[0]:
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    # check if we met our goals
                    if self.forehand_wins < self.forehand_bid_value:
                        # try to win
                        return self.HighestWinningCard(trick_cards, trump_suit, self.backhand)
                    else:
                        # try to lose
                        return self.ThrowTrick(trick_cards, trump_suit)
        else:
            self.backhand.sort_by_suit_and_rank()
            self.forehand.sort_by_suit_and_rank()
            if len(trick_cards)<2: # return a forehand card
                firstLosingCard = Tennis.GetFirstLosingCard(trick_cards, trump_suit, self.forehand.cards) # return the first winning card
                if not firstLosingCard: # if no winning card can be found, play the highest card
                    firstLosingCard = self.forehand.cards[0]
                return firstLosingCard
            else:
                # if the forehand is winning and needs to win, try to lose
                if (Tennis.GetWinningCard(trick_cards, trump_suit) == trick_cards.cards[1] and 
                    self.forehand_wins < self.forehand_bid_value):
                    return self.backhand.cards[-1] # play the lowest card
                else:
                    # check if we met our goals
                    if self.backhand_wins < self.backhand_bid_value:
                        # try to win
                        return self.HighestWinningCard(trick_cards, trump_suit, self.backhand)
                    else:
                        # try to lose
                        return self.ThrowTrick(trick_cards, trump_suit)