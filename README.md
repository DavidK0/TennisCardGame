# TennisCardGame
This is a python implementation of the two player card game [Tennis](https://etgdesign.com/games/tennis/). Tennis is essentially a two-player version of [Contact Bridge](https://en.wikipedia.org/wiki/Contract_bridge). The main difference is that players strive to match their bids for tricks in each of their two hands, their forehand and their backhand.

To play, clone the repository and run `python TennisDual.py`. This will simulator many randomly played rounds. In the future I will implement a human player option, more rule based AI players, and possibly a strategy guide.

# Players #
The base class for `TennisPlayer` as well as `RandomPlayer` are found in Tennis.py.
## Random Player ##
This player plays every move completely randomly.
## Avererage Bid Random Player ##
This plays tricks completely randomly, but it has a fixed-bid strategy.
## Agressive Player ##
Try to play a winning card every turn.

# Analysis #
When two random players compete, the average hand win is around 1.3 except for the leaders forehand which wins 8 on average. Each random player will make about 4.5 forehand errors and 5 backhand errors. When an otherwise random player simply bids as close as it can to those values, it makes only 1.4 errors in each hand.

This means that, if you and your opponent are playing randomly, you will average 3 errors just with a fixed-bid strategy.

So far Agressive Player is the champion Tennis AI.
