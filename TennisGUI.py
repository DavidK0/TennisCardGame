from Deck import Deck
from Deck import Card

import Tennis
from TennisLeaders import *
from TennisDealers import *

import random

import tkinter
from PIL import Image, ImageTk  # Importing modules for handling images


cards_images = Image.open("cards.png")  # Replace "image.png" with your image file
# Define the dimensions of each small card image
card_width = cards_images.width // 13
card_height = cards_images.height // 4
# Loop through rows and columns to crop and store individual card images
# This screates a map 'card_images' which maps from the string representation of a card to an image
card_images = {}
card_counter =  0
example_cards = Deck.Deck()
example_cards.reset()
for row in range(4):
    for col in range(13):
        left = col * card_width
        top = row * card_height
        right = left + card_width
        bottom = top + card_height

        card_image = cards_images.crop((left, top, right, bottom))
        
        # In the image, the Aces is next to the Duece
        index = card_counter - 1
        if card_counter % 13 == 0:
            index += 13
        
        card_images[str(example_cards.cards[index])] = card_image
        card_counter += 1

class HumanGUIPlayer(Tennis.TennisPlayer):
    def __init__(self, role, trump_suit):
        super().__init__(role, trump_suit)
        
        self.selected_card = None
        initial_width = 1200
        initial_height = 600
        self.root = tkinter.Tk()
        self.root.title("My Card Game")
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        # List to store references to PhotoImage objects
        self.photo_images = []
        
        # Running the main event loop
        self.loop_control = tkinter.IntVar()  # Variable to signal player action
    
    # Returns a card from the backhand
    def make_backhand_bid(self):
        self.backhand_card_buttons = self.create_deck_buttons(self.backhand, .5, .75)
    
        # Wait for the player to select a card
        while self.selected_card is None:
            self.root.update()  # Process events
            self.root.after(1)
            
        for button in self.backhand_card_buttons:
            button.config(state=tkinter.DISABLED)
            if button.card_str == str(self.selected_card):
                button.pack_forget()
        
        selected_card = self.selected_card
        self.selected_card = None  # Reset for the next turn
        return selected_card
        
    # Returns a card from the backhand
    def make_forehand_bid(self):
        self.forehand_card_buttons = self.create_deck_buttons(self.forehand, .25, .5)
    
        # Wait for the player to select a card
        while self.selected_card is None:
            self.root.update()  # Process events
            self.root.after(1)
            
        for button in self.forehand_card_buttons:
            button.config(state=tkinter.DISABLED)
            if button.card_str == str(self.selected_card):
                button.pack_forget()
        
        selected_card = self.selected_card
        self.selected_card = None  # Reset for the next turn
        return selected_card
    
    def play_forehand(self, trick_cards):
        for button in self.forehand_card_buttons:
            button.config(state=tkinter.NORMAL)  # Use the stored image

        # Wait for the player to select a card
        while self.selected_card is None:
            self.root.update()  # Process events
            self.root.after(1)

        for button in self.forehand_card_buttons:
            button.config(state=tkinter.DISABLED)
            if button.card_str == str(self.selected_card):
                button.pack_forget()

        selected_card = self.selected_card
        self.selected_card = None  # Reset for the next turn
        return selected_card
    
    def play_backhand(self, trick_cards):
        for button in self.backhand_card_buttons:
            button.config(state=tkinter.NORMAL)  # Use the stored image

        # Wait for the player to select a card
        while self.selected_card is None:
            self.root.update()  # Process events
            self.root.after(1)

        for button in self.backhand_card_buttons:
            button.config(state=tkinter.DISABLED)
            if button.card_str == str(self.selected_card):
                button.pack_forget()

        selected_card = self.selected_card
        self.selected_card = None  # Reset for the next turn
        return selected_card
    
    def create_deck_buttons(self, deck: Deck, x, y):
        # Clear previously displayed images
        self.photo_images.clear()

        deck_frame = tkinter.Frame(self.root)  # Create a new frame to hold the deck images
        
        buttons = [] # this is the list that will be returned
        
        for card in deck.cards:
            card_image = card_images[str(card)]  # Get the corresponding card image

            # Create a PhotoImage instance and keep a reference
            photo = ImageTk.PhotoImage(card_image)
            self.photo_images.append(photo)

            # Create a button with the card image
            card_button = tkinter.Button(deck_frame, image=photo, command=lambda c=card: self.card_button_click(c))
            card_button.photo = photo  # Store the PhotoImage reference in the button
            card_button.pack(side=tkinter.LEFT)  # Adjust padding as needed
            card_button.card_str = str(card)
            buttons.append(card_button)

        # Function to center the deck_frame
        def center_deck_frame(x=.5, y=.5, event=None):
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            # Calculate the position to center the deck_frame
            deck_frame_width = deck_frame.winfo_width()
            deck_frame_height = deck_frame.winfo_height()
            x = (window_width - deck_frame_width) * x
            y = (window_height - deck_frame_height) * y

            # Place the deck frame at the center of the root window
            deck_frame.place(x=x, y=y)

        # Bind the centering function to the <Configure> event
        #root.bind("<Configure>", center_deck_frame)
        self.root.bind("<Configure>", lambda event: center_deck_frame(x=x, y=y, event=event))
        

        # Initially center the deck_frame
        center_deck_frame()
        
        return buttons

    # Create a function to handle button clicks
    def card_button_click(self, card):
        self.selected_card = card


random_suit = random.choice(["C", "S", "H", "D"])
round_info = Tennis.PlayTennisRound(HumanGUIPlayer, MyFirstSmartDealer, random_suit, True)

