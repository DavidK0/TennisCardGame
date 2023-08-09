# TennisCardGame
This is a python implementation of the two player card game [Tennis](https://etgdesign.com/games/tennis/).

To play, clone the repository and run `python Tennis.py`. This will simulator 100,000 randomly played round. In the future I will implement trump suits, a human player option, a rule based AI player, more statistical analyses of the game, and possibly a strategy guide.

# Analysis #
When two random players compete, the average hand win is around 1.3 except for the leaders forehand which wins 8 on average. Each random player will make about 4.5 forehand errors and 5 backhand errors. When an otherwise random player simply bids as close as it can to those values, it makes only 1.4 errors in each hand.

This means that, if you and your opponent are playing randomly, you will average 3 errors just with a fixed-bid strategy.
