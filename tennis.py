from Deck import Deck

class Player:
    def __init__(self, name):
        # None of these value should ever be set by the player
        self.name = name
        self.forehand = None
        self.backhand = None
        self.forehand_bid_card = None
        self.forehand_bid_value = None
        self.backhand_bid_card = None
        self.backhand_bid_value = None
        self.forehand_wins = 0
        self.backhand_wins = 0
    
    # still lots of functions to put in

def main():
    player1 = Player("Player 1")
    player2 = Player("Player 2")
    players = [player1, player2]
    trump_suit = None
    
    deck = Deck() # create an empty deck
    deck.reset() # put 52 cards in and shuffle
    
    # deal 13 cards to each players hands
    for player in players:
        player.forehand = Deck()
        player.forehand.extend(deck.draw(13))
        player.backhand = Deck()
        player.backhand.extend(deck.draw(13))
    
    # the value of cards during a bid is different than during a trick
    def get_bid_value(card: Card):
        rank = card.numerical_rank()
        if rank == 13:
            return 0
        elif rank == 14:
            return 1
        else:
            return rank
    
    # a handy function to wrap-up bid info
    def get_player_bid_info(player: Player):
        backhand_bid_card = player.backhand_bid_card
        backhand_bid_value = player.backhand_bid_value
        backhand_bid = (backhand_bid_card, backhand_bid_value)
    
    # make bids
    for player in players: # backhand bids
        card = player.make_backhand_bid() # get the bid card
        player.backhand_bid_card = player.backhand.play(card) # set the bid card
        player.backhand_bid_value = get_bid_value(player.backhand_bid_card) # set the bid value
    for i in range(2) # forehand bids
        opponent_backhand_bid = get_player_bid_info(players[1-i]) # get info about the opponent's bid
        card = players[i].make_forehand_bid(opponent_backhand_bid) # get the bid card
        player.forehand_bid_card = player.forehand.play(card) # set the bid card
        player.forehand_bid_value = get_bid_value(player.forehand_bid_card) # set the bid value
    
    # play 12 tricks
    for trick in range(12):
        trick_cards = Deck()
        
        
        
        player[0].play()
        
        for player in players:
            player.
            played_card = player.play_card("Forehand", trick_suit, trick_cards)
            trick_suit = played_card.suit

        for player in players:
            played_card = player.play_card("Backhand", trick_suit, trick_cards)
            trick_suit = played_card.suit

        trick_cards.sort(key=lambda card: card.rank, reverse=True)
        trick_winner = trick_cards[0].suit
        print(f"{trick_winner} wins the trick.")
        trick_suit = None
        trick_cards = []

    # Calculate errors and scores
    for player in players:
        forehand_errors = abs(player.forehand_bid - len([card for card in trick_cards if card in player.forehand]))
        backhand_errors = abs(player.backhand_bid - len([card for card in trick_cards if card in player.backhand]))
        total_errors = forehand_errors + backhand_errors
        print(f"{player.name} has {total_errors} errors.")

if __name__ == "__main__":
    main()
