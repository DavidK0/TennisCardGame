# TennisCardGame
This is a python implementation of the two player card game [Tennis](https://etgdesign.com/games/tennis/).

To play, clone the repository and run `python TennisDual.py`. This will simulator 10,000 randomly played round. In the future I will implement a human player option, more rule based AI players, and possibly a strategy guide.

# Players #
## Random Player ##
Plays every move completely randomly
## Avererage Bid Random Player ##
Trys to bid close to a fixed-bid strategy but otherwise plays random
## Agressive Player ##
Try to play a winning card every turn.

# Analysis #
When two random players compete, the average hand win is around 1.3 except for the leaders forehand which wins 8 on average. Each random player will make about 4.5 forehand errors and 5 backhand errors. When an otherwise random player simply bids as close as it can to those values, it makes only 1.4 errors in each hand.

This means that, if you and your opponent are playing randomly, you will average 3 errors just with a fixed-bid strategy.

So far Agressive Player is the champion Tennis AI.
