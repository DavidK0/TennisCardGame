# This script contains a Q-network for training a DQN to play Tennis.

import torch
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class TennisLeaderQNetwork(torch.nn.Module):
    """
    A Deep Q-Network (DQN) model for the Tennis card game.
    
    Attributes:
    - input_size (int): The size of the input state tensor.
    - fc1, fc2, fc3 (torch.nn.Linear): Fully connected layers.
    - out (torch.nn.Linear): The output layer.
    
    Methods:
    - forward(state): Compute the Q-values for the given state.
    """
    
    def __init__(self):
        """
        Initialize the DQNTennis model and define its architecture.
        """
        super(TennisLeaderQNetwork, self).__init__()

        # Modify the input size
        self.input_size = 2*13*4 + 4*4 + 4*4 + 4 + 4

        # Define the neural network architecture
        self.fc1 = torch.nn.Linear(self.input_size, 512)
        self.fc2 = torch.nn.Linear(512, 256)
        self.fc3 = torch.nn.Linear(256, 128)
        
        # Output layer
        self.out = torch.nn.Linear(128, 52)  # Assuming 52 possible actions

    def forward(self, state):
        """
        Compute the Q-values for the given state using the DQN.
        
        Args:
        - state (torch.Tensor): The input state tensor.
        
        Returns:
        - torch.Tensor: The Q-values for each possible action.
        """
        # Mask out the dealer's hand information
        state = state.to(device)
        start = 2 * 13 * 4
        end = 4 * 13 * 4
        state = torch.cat((state[..., :start], state[..., end:]), dim=-1)

        x = torch.nn.functional.relu(self.fc1(state))
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))

        return self.out(x)
        
class TennisDealerQNetwork(torch.nn.Module):
    """
    A Deep Q-Network (DQN) model for the Tennis card game.
    
    Attributes:
    - input_size (int): The size of the input state tensor.
    - fc1, fc2, fc3 (torch.nn.Linear): Fully connected layers.
    - out (torch.nn.Linear): The output layer.
    
    Methods:
    - forward(state): Compute the Q-values for the given state.
    """
    
    def __init__(self):
        """
        Initialize the DQNTennis model and define its architecture.
        """
        super(TennisDealerQNetwork, self).__init__()

        # Modify the input size
        self.input_size = 2*13*4 + 4*4 + 4*4 + 4 + 4

        # Define the neural network architecture
        self.fc1 = torch.nn.Linear(self.input_size, 512)
        self.fc2 = torch.nn.Linear(512, 256)
        self.fc3 = torch.nn.Linear(256, 128)
        
        # Output layer
        self.out = torch.nn.Linear(128, 52)  # Assuming 52 possible actions

    def forward(self, state):
        """
        Compute the Q-values for the given state using the DQN.
        
        Args:
        - state (torch.Tensor): The input state tensor.
        
        Returns:
        - torch.Tensor: The Q-values for each possible action.
        """
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
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))

        return self.out(x)