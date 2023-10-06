# This script contains a Q-network for training a DQN to play Tennis.

import torch
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# A Deep Q-Network (DQN) model for the Tennis card game.
class TennisLeaderQNetwork(torch.nn.Module):
    
    def __init__(self):
        super(TennisLeaderQNetwork, self).__init__()

        # The input size
        self.input_size = 13*4 # forehand
        self.input_size += 13*4 # backhand
        self.input_size += + 4*4 # bids
        self.input_size += + 4*4 # trick
        self.input_size += + 4 # wins
        self.input_size += + 1 # trump suit

        # Define the neural network architecture
        self.fc1 = torch.nn.Linear(self.input_size, 128)
        self.out = torch.nn.Linear(128, 52)  # 52 possible actions

    # Compute the Q-values for the given state using the DQN.
    def forward(self, state):
        # Mask out the dealer's hand information
        state = state.to(device)
        start = 2 * 13 * 4
        end = 4 * 13 * 4
        state = torch.cat((state[..., :start], state[..., end:]), dim=-1)

        x = torch.nn.functional.relu(self.fc1(state))
        return self.out(x)
        
# A Deep Q-Network (DQN) model for the Tennis card game.
class TennisDealerQNetwork(torch.nn.Module):
    
    def __init__(self):
        super(TennisDealerQNetwork, self).__init__()

        # The input size
        self.input_size = 13*4 # forehand
        self.input_size += 13*4 # backhand
        self.input_size += + 4*4 # bids
        self.input_size += + 4*4 # trick
        self.input_size += + 4 # wins
        self.input_size += + 1 # trump suit

        # Define the neural network architecture
        self.fc1 = torch.nn.Linear(self.input_size, 128)
        self.out = torch.nn.Linear(128, 52)  # 52 possible actions

    # Compute the Q-values for the given state using the DQN.
    def forward(self, state):
        # Mask out the leader's hand information
        state = state.to(device)
        start = 2 * 13 * 4
        state = state[..., start:]
        
        # Check dealer's backhand bid and conditionally mask leader's backhand bid
        if torch.all(state[220:224] == 0):
            state[212:214] = 0

        # Check dealer's forehand bid and conditionally mask leader's forehand bid
        if torch.all(state[216:220] == 0):
            state[208:212] = 0

        x = torch.nn.functional.relu(self.fc1(state))
        return self.out(x)