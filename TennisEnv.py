# This is an implementation of the card game Tennis (https://etgdesign.com/games/tennis/).
# It is designed to be an environment playable by a reinforcement learning model.

# Standard library imports
import random

# Third-party imports
import torch
import numpy

# Local imports
from card_game_utils.Deck import Deck
from card_game_utils.TrickTaking import Trick

class TennisEnv:
    """
    TennisEnv represents the environment for the Tennis card game. 
    It is designed to be compatible with reinforcement learning algorithms.
    
    Attributes:
        trump_suit (str): The suit that is considered as trump for the current game.
        reward (int): The reward value for the current state of the game.
        done (bool): Flag indicating if the current game is finished.
        game_record (list): A record of all actions taken during the current game.
        deck (Deck): The deck of cards used in the game.
        trick_number (int): The current trick number in the game.
        current_trick (Trick): The current trick being played.
        action_space (list): List of all possible cards that can be played.
    """
    
    def __init__(self, leader, dealer, rewarded_player="leader"):
        """
        Initialize the Tennis environment.
        
        Args:
            trump_suit (str): The suit that is considered as trump for the current game.
            rewarded_player (str): Controls which player (leader or dealer) defines the reward for the environment.
                                   Must be either "leader" or "dealer".
        
        Raises:
            AssertionError: If the rewarded_player is not "leader" or "dealer".
        """

        # Ensure the rewarded player is either "leader" or "dealer"
        assert(rewarded_player in ["leader", "dealer"]), "rewarded_player must be either 'leader' or 'dealer'"
        self.rewarded_player = rewarded_player
        
        # Initialize game attributes
        self.trump_suit = random.choice(['C', 'S', 'H', 'D', None])
        self.done = False
        
        # Initialize the deck and the current trick
        self.deck = Deck()
        self.current_trick = Trick(self.trump_suit)  # Non-trump round
        
        # Define the action space based on a reference deck
        reference_deck = Deck()
        reference_deck.reset()
        self.action_space = reference_deck.cards  # List of all possible cards that can be played

        self.leader_q_network = leader
        self.dealer_q_network = dealer

    def reset(self):
        """
        Reset the Tennis environment to its initial state.
        
        This method initializes new players, resets the game state, shuffles the deck, 
        and deals cards to the players' backhands. It then returns the current state of the game.
        
        Returns:
            torch.Tensor: The current state of the game after reset.
        """
        # Initialize new players for the game
        self.leader = TennisPlayer("leader", self.trump_suit)
        self.dealer = TennisPlayer("dealer", self.trump_suit)
        
        # Reset game-related variables
        self.game_record = []
        self.done = False
        self.reward = 0
        self.trick_number = 0
        self.winner = None
        
        # Reset and shuffle the deck of cards
        self.deck.reset()
        self.deck.shuffle()
        
        # Deal 13 cards to each player's backhand and update the opponent's view of the hands
        for player in [self.leader, self.dealer]:
            player.backhand.add(self.deck.draw(13))
            for card in player.backhand.cards:
                player.opponent_both_hands.play(card)
        
        if self.rewarded_player == "dealer":
            self.step_helper(self.leader_q_network.choose_action(self))
        
        # Return the current state of the game
        return self.get_current_state()
    
    def step(self, action):

        next_state, reward, done, exit_cond = self.step_helper(action)
        if self.done:
            return next_state, reward, done, exit_cond

        if self.rewarded_player == "leader":
            return self.step_helper(self.dealer_q_network.choose_action(self))
        else:
            return self.step_helper(self.leader_q_network.choose_action(self))
        
    def step_helper(self, action):
        """
        Take a step in the Tennis environment based on the provided action.
        
        This method simulates the game's progression based on the action taken by the agent.
        It handles various game phases, such as bidding and playing cards, and updates the game state.
        
        Args:
            action (int): The action index representing the card to be played or bid.
        
        Returns:
            tuple: A tuple containing:
                - torch.Tensor: The next state of the game.
                - float: The reward obtained from taking the action.
                - bool: A flag indicating if the game is done.
                - dict: Additional information about the step (e.g., reason for termination).
        """
        
        # Get the card corresponding to the action
        played_card = self.action_space[action]
        self.game_record.append(played_card)
        
        # Sort all the cards in the players' hands
        self.leader.backhand.sort_by_rank()
        self.dealer.backhand.sort_by_rank()
        self.leader.forehand.sort_by_rank()
        self.dealer.forehand.sort_by_rank()
        
        # Check if the played card is a legal move
        assert(played_card in self.get_legal_moves())
        
        if self.leader.backhand_bid["card"] == None: # Leader forehand bid
            self.leader.backhand_bid["card"] = self.leader.backhand.play(played_card)
            self.leader.backhand_bid["value"] = self.leader.backhand_bid["card"].get_bid_value()
        elif self.dealer.backhand_bid["card"] == None: # Dealer forehand bid
            self.dealer.backhand_bid["card"] = self.dealer.backhand.play(played_card)
            self.dealer.backhand_bid["value"] = self.dealer.backhand_bid["card"].get_bid_value()
              
            # Revealed the backhand bids
            self.leader.opponent_both_hands.play(self.dealer.backhand_bid["card"])
            self.dealer.opponent_both_hands.play(self.leader.backhand_bid["card"])
            for player in [self.leader, self.dealer]:
                player.reveal_backhand_bids(self.leader.backhand_bid, self.dealer.backhand_bid)
                
            # Deal 13 cards to each player's forehand
            for player in [self.leader, self.dealer]:
                player.forehand = Deck()
                player.forehand.add(self.deck.draw(13))
                for card in player.forehand.cards:
                    player.opponent_both_hands.play(card)
        elif self.leader.forehand_bid["card"] == None: # Leader backhand bid
            self.leader.forehand_bid["card"] = self.leader.forehand.play(played_card)
            self.leader.forehand_bid["value"] = self.leader.forehand_bid["card"].get_bid_value()
        elif self.dealer.forehand_bid["card"] == None: # Dealer backhand bid
            self.dealer.forehand_bid["card"] = self.dealer.forehand.play(played_card)
            self.dealer.forehand_bid["value"] = self.dealer.forehand_bid["card"].get_bid_value()
            
            # Revealed the forehand bids
            self.leader.opponent_both_hands.play(self.dealer.forehand_bid["card"])
            self.dealer.opponent_both_hands.play(self.leader.forehand_bid["card"])
            for player in [self.leader, self.dealer]:
                player.reveal_forehand_bids(self.leader.forehand_bid, self.dealer.forehand_bid)
        else:
            # First card
            if len(self.current_trick) == 0:
                self.leader.forehand.play(played_card)
                self.dealer.opponent_both_hands.play(played_card)
                self.current_trick.add_card(played_card)
            
            # Second card
            elif len(self.current_trick) == 1:
                self.dealer.forehand.play(played_card)
                self.leader.opponent_both_hands.play(played_card)
                self.current_trick.add_card(played_card)
            
            # Third card
            elif len(self.current_trick) == 2:
                self.leader.backhand.play(played_card)
                self.dealer.opponent_both_hands.play(played_card)
                self.current_trick.add_card(played_card)
            
            # Fourth card
            elif len(self.current_trick) == 3:
                self.dealer.backhand.play(played_card)
                self.current_trick.add_card(played_card)
                self.leader.opponent_both_hands.play(played_card)
                
                # Find Trick winner
                if self.current_trick.winning_index == 0:
                    self.leader.forehand_wins += 1
                    self.dealer.opponent_forehand_wins+= 1
                elif self.current_trick.winning_index == 1:
                    self.dealer.forehand_wins += 1
                    self.leader.opponent_forehand_wins += 1
                elif self.current_trick.winning_index == 2:
                    self.leader.backhand_wins += 1
                    self.dealer.opponent_backhand_wins += 1
                elif self.current_trick.winning_index == 3:
                    self.dealer.backhand_wins += 1
                    self.leader.opponent_backhand_wins += 1
                
                # Reset the trick
                self.current_trick = Trick(self.trump_suit)
                
                # Check if the game is over
                if len(self.leader.forehand) == 0:
                    self.done = True




        # New reward
        if not self.done:
            self.reward = 0
        else:
            # leader score
            leader_forehand_bid_difference = abs(self.leader.forehand_bid["value"] - self.leader.forehand_wins)
            leader_backhand_bid_difference = abs(self.leader.backhand_bid["value"] - self.leader.backhand_wins)
            leader_bid_difference = leader_forehand_bid_difference + leader_backhand_bid_difference
        
            # dealer score
            dealer_forehand_bid_difference = abs(self.dealer.forehand_bid["value"] - self.dealer.forehand_wins)
            dealer_backhand_bid_difference = abs(self.dealer.backhand_bid["value"] - self.dealer.backhand_wins)
            dealer_bid_difference = dealer_forehand_bid_difference + dealer_backhand_bid_difference

            if self.rewarded_player == "leader":
                self.reward = dealer_bid_difference-leader_bid_difference
            else:
                self.reward = leader_bid_difference-dealer_bid_difference
            self.reward /= 24

            if self.rewarded_player == "leader":
                if self.reward > 0:
                    self.winner = "leader"
                elif self.reward < 0:
                    self.winner = "dealer"
                else:
                    self.winner = "draw"
            else:
                if self.reward > 0:
                    self.winner = "dealer"
                elif self.reward < 0:
                    self.winner = "leader"
                else:
                    self.winner = "draw"
            

        # Old reward
        #if self.dealer.forehand_bid["card"] != None:
        #    # leader score
        #    leader_forehand_bid_difference = abs(self.leader.forehand_bid["value"] - self.leader.forehand_wins)
        #    leader_backhand_bid_difference = abs(self.leader.backhand_bid["value"] - self.leader.backhand_wins)
        #    leader_bid_difference = leader_forehand_bid_difference + leader_backhand_bid_difference
        #    
        #    # dealer score
        #    dealer_forehand_bid_difference = abs(self.dealer.forehand_bid["value"] - self.dealer.forehand_wins)
        #    dealer_backhand_bid_difference = abs(self.dealer.backhand_bid["value"] - self.dealer.backhand_wins)
        #    dealer_bid_difference = dealer_forehand_bid_difference + dealer_backhand_bid_difference
        #    
        #    if self.rewarded_player == "leader":
        #        self.reward = dealer_bid_difference-leader_bid_difference
        #    else:
        #        self.reward = leader_bid_difference-dealer_bid_difference
        #    self.reward /= 24 # normalize the reward
        #else:
        #    self.reward = -24
        
        return self.get_current_state(), self.reward, self.done, {}
    
    def render(self):
        """
        Render the current state of the Tennis game.
        
        This method displays the current game state, including the trump suit, players' hands, bids, 
        the current trick, and the scores. It provides a visual representation of the game's progress.
        """
        # Display the trump suit
        print(f"Trump suit: {self.trump_suit}".ljust(30))
        
        # Display the backhands of both players
        print(f"Player 1 backhand: {self.leader.backhand}")
        print(f"Player 2 backhand: {self.dealer.backhand}")
        
        # Display the forehands of both players
        print(f"Player 1 forehand: {self.leader.forehand}")
        print(f"Player 2 forehand: {self.dealer.forehand}")
        
        # Display the bids made by both players
        print(f"Player 1 bids: [{self.leader.forehand_bid['card']}, {self.leader.backhand_bid['card']}]")
        print(f"Player 2 bids: [{self.dealer.forehand_bid['card']}, {self.dealer.backhand_bid['card']}]")
        
        # Display the current trick
        print(f"Current trick: {self.current_trick}")
        
        # Display the scores of both players
        # Calculate the total error for each player and display it
        if self.dealer.forehand_bid["card"] != None:
            p1_total_error = abs(self.leader.forehand_bid["value"] - self.leader.forehand_wins) + \
                             abs(self.leader.backhand_bid["value"] - self.leader.backhand_wins)
            p2_total_error = abs(self.dealer.forehand_bid["value"] - self.dealer.forehand_wins) + \
                             abs(self.dealer.backhand_bid["value"] - self.dealer.backhand_wins)
            print(f"Leader score: [{self.leader.forehand_bid['value']}, {self.leader.backhand_bid['value']}] - "
                  f"[{self.leader.forehand_wins}, {self.leader.backhand_wins}] = {p1_total_error}")
            print(f"Dealer score: [{self.dealer.forehand_bid['value']}, {self.dealer.backhand_bid['value']}] - "
                  f"[{self.dealer.forehand_wins}, {self.dealer.backhand_wins}] = {p2_total_error}")
    
    def seed(self, seed_value=None):
        """
        Set the seed for random number generators.
        
        This method sets the seed for both Python's built-in random module and numpy's random module.
        It ensures reproducibility in the game's random events.
        
        Args:
            seed_value (int, optional): The value to use as the seed. If None, the RNGs will be seeded randomly.
        
        Returns:
            list: A list containing the provided seed value.
        """
        random.seed(seed_value)
        np.random.seed(seed_value)  # Seed numpy's random number generator
        # If you use other random number generators, set their seeds here too
        return [seed_value]

    
    def get_current_state(self):  
        def get_card_tensor(card):
            if not card:
                return torch.zeros(4)  
            suit_vector = torch.zeros(4)
            suit_mapping = {"C": 0, "D": 1, "H": 2, "S": 3}
            if card.suit in suit_mapping:
                suit_vector[suit_mapping[card.suit]] = card.numeric_rank() / 14
            
            return suit_vector

        # Initialize an empty list to store all tensors
        state_tensors = []

        # Process hands
        for hand in [self.leader.forehand, self.leader.backhand, self.dealer.forehand, self.dealer.backhand]:
            tensor = torch.zeros(13, 4)  # Create a 13x5 tensor filled with zeros
            for idx, card in enumerate(hand.cards):
                tensor[idx] = get_card_tensor(card).clone().detach()
            state_tensors.append(tensor)

        # Process bids
        for bid in [
           self.leader.forehand_bid,
           self.leader.backhand_bid,
           self.dealer.forehand_bid,
           self.dealer.backhand_bid
        ]:
            value = bid.get("value", 0)
            if value == None:
                value = 0 # This value is equal to an actual bid of zero
            else:
                # Normalize the bid
                value = value / 12
            card_tensor = get_card_tensor(bid.get("card"))
            state_tensors.append(card_tensor)

        # Process current trick
        trick_list = [get_card_tensor(card) for card in self.current_trick.cards]
        while len(trick_list) < 4:
            trick_list.append(torch.zeros(4))
        state_tensors.extend(trick_list)
        
        # Process wins
        wins_info = torch.tensor([self.leader.forehand_wins / 12, self.leader.backhand_wins / 12, self.dealer.forehand_wins / 12, self.dealer.backhand_wins / 12])
        state_tensors.append(wins_info)

        # Trump suit
        trump_vector = torch.zeros(4)
        suit_mapping = {"C": 0, "D": 1, "H": 2, "S": 3}
        if self.trump_suit in suit_mapping:
            trump_vector [suit_mapping[self.trump_suit]] = 1
        state_tensors.append(trump_vector)

        # Flatten and concatenate all tensors to form the final state tensor
        state_tensor = torch.cat([tensor.flatten() for tensor in state_tensors])

        return state_tensor
    
    def get_legal_moves(self):
        """
        Determine the legal moves available to the current player.
        
        This method checks the current game state and determines which cards can be legally played 
        or bid by the current player. It considers the game phase (bidding or playing) and the current trick.
        
        Returns:
            list: A list of legal moves available to the current player.
        """
        # Check if the leader has made their forehand bid
        if self.leader.backhand_bid["card"] == None:
            return self.leader.backhand
        # Check if the dealer has made their forehand bid
        elif self.dealer.backhand_bid["card"] == None:
            return self.dealer.backhand
        # Check if the leader has made their backhand bid
        elif self.leader.forehand_bid["card"] == None:
            return self.leader.forehand
        # Check if the dealer has made their backhand bid
        elif self.dealer.forehand_bid["card"] == None:
            return self.dealer.forehand
        else:
            # Determine legal moves based on the number of cards played in the current trick
            if len(self.current_trick) == 0:
                return self.current_trick.get_legal_moves(self.leader.forehand)
            elif len(self.current_trick) == 1:
                return self.current_trick.get_legal_moves(self.dealer.forehand)
            elif len(self.current_trick) == 2:
                return self.current_trick.get_legal_moves(self.leader.backhand)
            elif len(self.current_trick) == 3:
                return self.current_trick.get_legal_moves(self.dealer.backhand)
    
    # Plays a random moe
    def random_step(self):
        return self.step_helper(self.action_space.index(random.choice(self.get_legal_moves())))
    

# This class is the base class for Tennis players.
class TennisPlayer:
    def __init__(self, role, trump_suit):
        # None of these value should ever be set by the manually
        
        self.trump_suit = trump_suit
        
        # Information about this player #
        
        self.role = role # 'leader' or 'dealer'
        
        # One deck for each hand
        self.forehand = Deck()
        self.backhand = Deck()
        
        # One dict (keys = 'card', 'value') for each hand
        # The data types for 'card' and 'value' are Card and int respectively
        self.forehand_bid = {"card": None, "value": None}
        self.backhand_bid = {"card": None, "value": None}
        
        # One int for each hand
        self.forehand_wins = 0
        self.backhand_wins = 0
        
        # Information about the opponent #
        
        # One dict for the all the cards the opponent has
        self.opponent_both_hands = Deck()
        self.opponent_both_hands.reset()
        
        # One dict (keys = 'card', 'value') for each hand
        self.opponent_forehand_bid = None
        self.opponent_backhand_bid = None
        
        # One int for each hand
        self.opponent_forehand_wins = 0
        self.opponent_backhand_wins = 0
    
    # Reveal the forehand bids
    def reveal_forehand_bids(self, leader_forehand_bid, dealer_forehand_bid):
        if self.role == "leader":
            self.forehand_bid = leader_forehand_bid
            self.opponent_forehand_bid = dealer_forehand_bid
        else:
            self.forehand_bid = dealer_forehand_bid
            self.opponent_forehand_bid = leader_forehand_bid
    
    # Reveal the backhand bids
    def reveal_backhand_bids(self, leader_backhand_bid, dealer_backhand_bid):
        if self.role == "leader":
            self.backhand_bid = leader_backhand_bid
            self.opponent_backhand_bid = dealer_backhand_bid
        else:
            self.backhand_bid = dealer_backhand_bid
            self.opponent_backhand_bid = leader_backhand_bid