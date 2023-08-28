# This script allows a human to play Tennis with a GUI

from Deck import Deck
from Deck import Card

import Tennis
from TennisLeaders import *
from TennisDealers import *

import random

import tkinter
from PIL import Image, ImageTk  # Importing modules for handling images

cards_images = Image.open("cards.png")  # A sprite map of cards
card_back =  Image.open("card_back.jpg")  # The back of cards

# Crop the sprite map of cards into individual cards
# This creates a map 'card_images' which maps from the string representation of a card to an image
card_images = {}
card_size = (cards_images.width // 13, cards_images.height // 4) # The dimensions of each small card image
example_cards = Deck.Deck()
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

# This class allows a human play to play Tennis against an AI using a GUI
class HumanGUIPlayer(Tennis.TennisPlayer):
    def __init__(self, role, trump_suit):
        super().__init__(role, trump_suit)
        
        # Create a tkinter window
        self.root = tkinter.Tk()
        self.root.title("Tennis GUI")
        
        # Size the window
        initial_width = 800
        initial_height = 600
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        self.selected_card = None # This is used to track clicking cards
        self.GUI_WAIT_TIME = 1 # Miliseconds to wait between GUI updates
        
        # Diplay text
        self.display_text = tkinter.StringVar()
        label = tkinter.Label(self.root, textvariable=self.display_text)
        self.display_text.set("You are playing as the LEADER")
        label.place(x=400,y=300)
    
    # This allows the player to click on some card
    def wait_for_card_click(self, card_buttons):
        # Enable the card buttons
        for button in card_buttons:
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
    
    def display_wins():
        if hasattr(self, "win_card_buttons"):
            for button in self.win_card_buttons:
                button.destroy()
        self.win_card_buttons = []
        
        if hasattr(self, "opponent_win_card_buttons"):
            for button in self.opponent_win_card_buttons:
                button.destroy()
        self.opponent_win_card_buttons = []
        
    
    # Returns a card from the backhand
    def make_backhand_bid(self):
        self.backhand_card_buttons = self.create_deck_buttons(self.backhand, 0)
        return self.wait_for_card_click(self.backhand_card_buttons)
        
    # Returns a card from the backhand
    def make_forehand_bid(self):
        self.forehand_card_buttons = self.create_deck_buttons(self.forehand, 1)
        bid_cards = Deck.Deck()
        opponent_bid_cards = Deck.Deck()
        bid_cards.add(self.backhand_bid["card"])
        opponent_bid_cards.add(self.opponent_backhand_bid["card"])
        self.bids_card_buttons = self.create_deck_buttons(bid_cards, 4)
        self.opponent_bids_card_buttons = self.create_deck_buttons(opponent_bid_cards, 3)
    
        return self.wait_for_card_click(self.forehand_card_buttons)
    
    def play_forehand(self, trick_cards):
        self.diplay_trick_cards(trick_cards)
        return self.wait_for_card_click(self.forehand_card_buttons)
    
    def play_backhand(self, trick_cards):
        self.diplay_trick_cards(trick_cards)
        return self.wait_for_card_click(self.backhand_card_buttons)
    
    def diplay_trick_cards(self, trick_cards):
        if hasattr(self, "trick_card_buttons"):
            for button in self.trick_card_buttons:
                button.destroy()
        self.trick_card_buttons = self.create_deck_buttons(trick_cards, 2, False)
        for button in self.bids_card_buttons:
            button.destroy()
        for button in self.opponent_bids_card_buttons:
            button.destroy()
        bid_cards = Deck.Deck()
        opponent_bid_cards = Deck.Deck()
        bid_cards.add(self.forehand_bid["card"])
        opponent_bid_cards.add(self.opponent_forehand_bid["card"])
        bid_cards.add(self.backhand_bid["card"])
        opponent_bid_cards.add(self.opponent_backhand_bid["card"])
        self.bids_card_buttons = self.create_deck_buttons(bid_cards, 4, False)
        self.opponent_bids_card_buttons = self.create_deck_buttons(opponent_bid_cards, 3, False)
    
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
    
    def create_deck_buttons(self, deck: Deck, pos, select_card = True):
        # Clear previously displayed images
        #self.photo_images.clear()

        deck_frame = tkinter.Frame(self.root)  # Create a new frame to hold the deck images
        
        buttons = [] # this is the list that will be returned
        
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
            
            photo = self.get_card_photo(card, rotate)

            # This button will do nothing if 'select_card' is set to calse
            function = None
            if select_card:
                function = lambda c=card: self.card_button_click(c)
            
            # Create a button with the card image
            card_button = tkinter.Button(deck_frame, image=photo, command=function)
            card_button.photo = photo  # Store the PhotoImage reference in the button
            card_button.pack(side=tkinter.LEFT)  # Adjust padding as needed
            card_button.card_str = str(card)
            buttons.append(card_button)
            
            card_counter += 1
        
        self.root.update_idletasks() 
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        if pos == 0:
            y = window_height - card_size[1]
        elif pos == 1:
            y = window_height - card_size[1] * 2
        elif pos == 2:
            y = window_height - card_size[1] * 3
        elif pos == 3:
            y = window_height - card_size[1] * 4
        elif pos == 4:
            y = window_height - card_size[1] * 5
        x = 0
        
        deck_frame.place(x=x, y=y)
        
        return buttons

    # Create a function to handle button clicks
    def card_button_click(self, card):
        self.selected_card = card

if __name__ == "__main__":
    random_suit = random.choice(["C", "S", "H", "D"])
    round_info = Tennis.PlayTennisRound(HumanGUIPlayer, MyFirstSmartDealer, random_suit, True)