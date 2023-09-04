# This script allows a human to play Tennis with a GUI

from Deck import Deck
from Deck import Card

import Tennis

import random

import tkinter
from PIL import Image, ImageTk  # Importing modules for handling images

cards_images = Image.open("cards.png")  # A sprite map of cards
#card_back =  Image.open("card_back.jpg")  # The back of cards

# Crop the sprite map of cards into individual cards
# This creates a map 'card_images' which maps from the string representation of a card to an image
card_images = {}

card_resize_factor = .2
card_size = (cards_images.width // 13, cards_images.height // 5) # The dimensions of each small card image

example_cards = Deck()
example_cards.reset()

for row in range(4):
    for col in range(13):
        left, top = col * card_size[0], row * card_size[1]
        right, bottom = left + card_size[0], top + card_size[1]
        card_image = cards_images.crop((left, top, right, bottom))
       
        index = row * 13 + col - 1  # In the image, the Aces is next to the Duece
        if col == 0:
            index += 13
        
        card_images[str(example_cards.cards[index])] = card_image
card_images["back"] = card_images["AS"]

for card_key in card_images:
    card_images[card_key] = card_images[card_key].resize((int(card_size[0] * card_resize_factor), int(card_size[1] * card_resize_factor)))

# This class allows a human play to play Tennis against an AI using a GUI
class HumanGUIPlayer(Tennis.TennisPlayer):
    def __init__(self, role, trump_suit):
        super().__init__(role, trump_suit)
        
        # Create a tkinter window
        self.root = tkinter.Tk()
        self.root.title("Tennis GUI")
        
        # Size the window
        initial_width = 1000
        initial_height = 600
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        self.selected_card = None # This is used to track clicking cards
        self.GUI_WAIT_TIME = 1 # Miliseconds to wait between GUI updates
        
        # Diplay text
        self.display_text = tkinter.StringVar()
        label = tkinter.Label(self.root, textvariable=self.display_text)
        self.display_text.set(f"You are playing as the {self.role}")
        label.place(x=300,y=350)
    
        spacing = 95
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Opponent's\nhands"))
        label.place(x=0,y=50)
        
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Your bids\nand wins"))
        label.place(x=0,y=50 + spacing * 1)
        
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Opponent's bids\nand wins"))
        label.place(x=0,y=50 + spacing * 2)
        
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Current\ntrick"))
        label.place(x=0,y=50 + spacing * 3)
        
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Your\nforehand"))
        label.place(x=0,y=50 + spacing * 4)
        
        label = tkinter.Label(self.root, textvariable=tkinter.StringVar(self.root, f"Your\nbackhand"))
        label.place(x=0,y=50 + spacing * 5)
    
    # This allows the player to click on some card
    def wait_for_card_click(self, card_buttons, legal_moves=None):
        # Enable the card buttons
        for button in card_buttons:
            if not legal_moves or button.card_str in [str(card) for card in legal_moves]:
                button.config(state=tkinter.NORMAL)

        # Wait for the player to click on a card button
        while self.selected_card is None:
            self.root.update()  # Process events
            self.root.after(self.GUI_WAIT_TIME)
        
        # Disable the button cards
        for button in card_buttons:
            button.config(state=tkinter.DISABLED)
            
            # Delete (forget) the seleceted card
            if button.card_str == str(self.selected_card):
                button.pack_forget()
        
        # Reset the selected card and return it
        selected_card = self.selected_card
        self.selected_card = None
        return selected_card
    
    def display_wins(self):
        if hasattr(self, "win_card_buttons"):
            for button in self.win_card_buttons:
                button.destroy()
        self.win_card_buttons = []
        
        if hasattr(self, "opponent_win_card_buttons"):
            for button in self.opponent_win_card_buttons:
                button.destroy()
        self.opponent_win_card_buttons = []
        
        wins_deck = Deck()
        for i in range(self.forehand_wins):
            wins_deck.add(Card("back", ""))
        for i in range(self.backhand_wins):
            wins_deck.add(Card("back", ""))
        
        opponent_wins_deck = Deck()
        for i in range(self.opponent_forehand_wins):
            opponent_wins_deck.add(Card("back", ""))
        for i in range(self.opponent_backhand_wins):
            opponent_wins_deck.add(Card("back", ""))
            
        deck_frame, self.win_card_buttons = self.display_deck(wins_deck, 5)
        deck_frame, self.opponent_win_card_buttons = self.display_deck(opponent_wins_deck, 6)
    
    # Returns a card from the backhand
    def make_backhand_bid(self):
        self.backhand.sort_by_rank()
        deck_frame, self.backhand_card_buttons = self.display_deck(self.backhand, 0, True)
        deck_frame.grid(column=0, row=5)
        self.display_opponent_both_hands()
        
        return self.wait_for_card_click(self.backhand_card_buttons)
        
    # Returns a card from the backhand
    def make_forehand_bid(self):
        self.forehand.sort_by_rank()
        deck_frame, self.forehand_card_buttons = self.display_deck(self.forehand, 1, True)
        deck_frame.grid(column=0, row=4)
        self.display_opponent_both_hands()
        
        bid_cards = Deck()
        opponent_bid_cards = Deck()
        bid_cards.add(self.backhand_bid["card"])
        opponent_bid_cards.add(self.opponent_backhand_bid["card"])
        deck_frame, self.bids_card_buttons = self.display_deck(bid_cards, 4)
        deck_frame.grid(column=0, row=1)
        deck_frame, self.opponent_bids_card_buttons = self.display_deck(opponent_bid_cards, 3)
        deck_frame.grid(column=0, row=2)
    
        return self.wait_for_card_click(self.forehand_card_buttons)
    
    def play_forehand(self, trick):
        self.forehand.sort_by_rank()
        self.diplay_trick_cards(trick)
        self.display_wins()
        self.display_opponent_both_hands()
        return self.wait_for_card_click(self.forehand_card_buttons, trick.get_legal_moves(self.forehand))
    
    def play_backhand(self, trick):
        self.backhand.sort_by_rank()
        self.diplay_trick_cards(trick)
        self.display_wins()
        self.display_opponent_both_hands()
        return self.wait_for_card_click(self.backhand_card_buttons, trick.get_legal_moves(self.backhand))
    
    def diplay_trick_cards(self, trick_cards):
        if hasattr(self, "trick_card_buttons"):
            for button in self.trick_card_buttons:
                button.destroy()
        deck_frame, self.trick_card_buttons = self.display_deck(trick_cards, 2)
        deck_frame.grid(column=0, row=3)
        for button in self.bids_card_buttons:
            button.destroy()
        for button in self.opponent_bids_card_buttons:
            button.destroy()
        bid_cards = Deck()
        opponent_bid_cards = Deck()
        bid_cards.add(self.forehand_bid["card"])
        opponent_bid_cards.add(self.opponent_forehand_bid["card"])
        bid_cards.add(self.backhand_bid["card"])
        opponent_bid_cards.add(self.opponent_backhand_bid["card"])
        
        deck_frame, self.bids_card_buttons = self.display_deck(bid_cards, 4)
        deck_frame.grid(column=0, row=1)
        deck_frame, self.opponent_bids_card_buttons = self.display_deck(opponent_bid_cards, 3)
        deck_frame.grid(column=0, row=2)
    
    def display_opponent_both_hands(self):
        if hasattr(self, "opponent_both_hands_images"):
            for button in self.opponent_both_hands_images:
                button.destroy()
        self.opponent_both_hands_images = []
            
        deck_frame, self.opponent_both_hands_images = self.display_deck(self.opponent_both_hands, 7)
    
    def get_card_photo(self, card, rotate=False):
        card_image = card_images[str(card)]  # Get the corresponding card image
        
        # Handle rotation and cropping
        if rotate:
            card_image = card_image.rotate(90, expand=True)
            
        # Handle cropping
        width, height = card_image.size
        card_image = card_image.crop((0, 0, width // 2, height))
        
        # Create and return the PhotoImage instance
        return ImageTk.PhotoImage(card_image)
    
    # Dsplays the given deck at the give 'pos', and optionally makes the cards clickable
    def display_deck(self, deck: Deck, pos, clickable = False):
        deck_frame = tkinter.Frame(self.root)  # Create a new frame to hold the deck images
        cards_objects = [] # this is the list that will be returned
        photo = None
        card_counter = 0
        for card in deck.cards:
            # Decide rotation
            rotate = False
            if pos == 0:
                rotate = True
            elif pos == 2 and card_counter > 2:
                rotate = True
            elif pos == 3 and card_counter == len(deck) - 1:
                rotate = True
            elif pos == 4 and card_counter == len(deck) - 1:
                rotate = True
            elif pos == 5 and card_counter >= self.forehand_wins:
                rotate = True
            elif pos == 6 and card_counter >= self.opponent_forehand_wins:
                rotate = True
            
            photo = self.get_card_photo(card, rotate)

            # This button will do nothing if 'select_card' is set to false
            function = None
            if clickable:
                function = lambda c=card: self.card_button_click(c)
                card_button = tkinter.Button(deck_frame, image=photo, command=function)
            else:
                card_button = tkinter.Label(deck_frame, image=photo)
            
            # Create a button with the card image
            card_button.photo = photo  # Store the PhotoImage reference in the button
            card_button.pack(side=tkinter.LEFT)  # Adjust padding as needed
            card_button.card_str = str(card)
            cards_objects.append(card_button)
            
            card_counter += 1
        
        self.root.update_idletasks() 
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        return deck_frame, cards_objects

    # Create a function to handle button clicks
    def card_button_click(self, card):
        self.selected_card = card

if __name__ == "__main__":
    random_suit = random.choice(["C", "S", "H", "D"])
    round_info = Tennis.PlayTennisRound(HumanGUIPlayer, Tennis.RandomTennisPlayer, random_suit, False)
    
    leader_bids = round_info[0][0][0]
    leader_wins = round_info[0][0][1]
    leader_errors = round_info[0][0][2]
    
    dealer_bids = round_info[0][1][0]
    dealer_wins = round_info[0][1][1]
    dealer_errors = round_info[0][1][2]
    
    
    def nice_format(num_pair):
        return [f"{(x):.1f}" for x in num_pair]

    print(f"Results:")
    if round_info[1] == 0:
        print("The leader won")
    elif round_info[1] == 1:
        print("The dealer won")
    else:
        print("It was a tie")
    print()
    print(f"Leader:")
    print(f"Bids: {nice_format(leader_bids)}")
    print(f"Wins: {nice_format(leader_wins)}")
    print(f"Errors: {nice_format(leader_errors)}")
    print()
    print(f"Dealer:")
    print(f"Bids: {nice_format(dealer_bids)}")
    print(f"Wins: {nice_format(dealer_wins)}")
    print(f"Errors: {nice_format(dealer_errors)}")