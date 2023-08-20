import Tennis
from Deck import Deck
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
            return self.LowestWinningCard(trick_cards, self.backhand)

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
                return self.HighestWinningCard(trick_cards, self.backhand)
            else:
                # try to lose
                return self.ThrowTrick(trick_cards)

class MySecondSmartLeader(Tennis.TennisPlayer):
    # The subset of the backhand that this player will win with
    def __init__(self, role, trump_suit):
        super().__init__(role, trump_suit)
        self.winning_backhand_pairs = []
        
        # Use this to see how this play makes decisions
        self.verbose = False
        if self.verbose:
            print()
    
    def make_backhand_bid(self):
        average_rank = self.backhand.average_numeric_rank()
        target_bid = average_rank - 6
        return self.backhand.closest_bid_card(target_bid)

    def make_forehand_bid(self):
        # assume the opponent will bid 0 on the forehand
        target_bid = 12 - self.backhand_bid["value"] - self.opponent_backhand_bid["value"]
        
        # This is an adhoc solution to combat AgressiveDealer
        if self.opponent_backhand_bid["value"] == 3:
            target_bid -= 2
        
        return self.forehand.closest_bid_card(target_bid)
    
    # For each card that we expect to win from the backhand, find a matching card from the
    #   forehand that will lose and that will allow the backhand to win
    def create_winning_backhand_pairs(self):
        # Do nothing if there are already the correct number of pairs
        curr_backhand_error = self.backhand_bid["value"] - self.backhand_wins
        num_pairs = min(curr_backhand_error, len(self.backhand))
        if len(self.winning_backhand_pairs) == num_pairs:
            return
        
        # Reset the pairs
        self.winning_backhand_pairs = []
        
        # Sort backhand by rank
        self.backhand.sort_by_rank() # highest first
        self.forehand.sort_by_rank(True) # lowest first
        
        # Check every card pair, prefering high backhand and low forehand cards
        for bachkand_card in self.backhand.cards:
            for forehand_card in self.forehand.cards:
                # Skip this forehand card if it is already being used
                if forehand_card in [x[0] for x in self.winning_backhand_pairs]:
                    continue
                # Use this backhand card if it beats the forehand
                if not self.CompareCards(forehand_card, bachkand_card):
                    # Winning pair found
                    self.winning_backhand_pairs.append((forehand_card, bachkand_card))
                    break
        
        # Sort the pairs so the highest backhand cards are used
        self.winning_backhand_pairs = sorted(self.winning_backhand_pairs, key = lambda x: x[1].numeric_rank(), reverse = True)
        
        # Select as many pairs as neccesary
        # If there are not enough, that probably means this player will get an error
        self.winning_backhand_pairs = self.winning_backhand_pairs[:num_pairs]
        if self.verbose:
            print(self.trump_suit,[(str(x[0]), str(x[1])) for x in self.winning_backhand_pairs],end="")
            print(f" bid: {self.backhand_bid['value']}, wins: {self.backhand_wins}")
        
    def play_forehand(self, trick_cards):
        self.create_winning_backhand_pairs()
        
        # Allow the backhand to win
        if len(self.backhand) == len(self.winning_backhand_pairs):
            return self.winning_backhand_pairs[0][0]
        
        # Play a random card
        reserved_forehand_cards = [x[0] for x in self.winning_backhand_pairs]
        return random.choice([x for x in self.forehand.cards if x not in reserved_forehand_cards])
    
    def play_backhand(self, trick_cards):
        self.create_winning_backhand_pairs()
        
        # Win as back hand if it is time
        if len(self.backhand) == len(self.winning_backhand_pairs):
            return self.winning_backhand_pairs[0][1]
        
        # Play a losing card that isn't reserved
        self.backhand.sort_by_suit_and_rank()
        reserved_backhand_cards = [x[1] for x in self.winning_backhand_pairs]
        unreserved_cards = [x for x in self.backhand.cards if x not in reserved_backhand_cards]
        for card in unreserved_cards:
            new_trick = Deck()
            new_trick.cards = [x for x in trick_cards.cards]
            new_trick.add(card)
            if Tennis.GetWinningCard(new_trick, self.trump_suit) != card:
                return card
        
        # Play a random card
        return random.choice(unreserved_cards)