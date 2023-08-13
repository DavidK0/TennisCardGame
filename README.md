# TennisCardGame
This is a python implementation of the two player card game [Tennis](https://etgdesign.com/games/tennis/). Tennis is essentially a two-player version of [Contact Bridge](https://en.wikipedia.org/wiki/Contract_bridge). The main difference is that players strive to match their bids for tricks in each of their two hands, their forehand and their backhand.

To play, clone the repository and run `python TennisDual.py`. This will simulator many randomly played rounds. In the future I will implement a human player option, more rule based AI players, and possibly a strategy guide.

# Players #
The base class for `TennisPlayer` as well as `RandomPlayer` are found in Tennis.py.
## Random Player ##
This player plays every move completely randomly.
## Avererage Bid Random Player ##
This player plays tricks completely randomly, but it has a fixed-bid strategy, trying to get as close as possible to pre-chosen bid values. As the leader \(non-dealer\) it will bid close to 8 on the forehand and 1 on the backhand. As the dealer it will always bid close to 1.
## Agressive Player ##
This player has a fixed-bid strategy at \(9, 1\) as the leader and \(5, 2\) as the dealer. During tricks as the leader, the forehand cards will be played in order by rank higest to lowest, and the backhand will try to win any trick it can with the lowest winning card, unless it has no winning cards or its forehand is winning, in which case it will play it's lowest card. As the dealer the forehand plays it's lowest winning card or else it's lowest card, and the backhand will play it's lowesting winning card as long as its forehand is not winning, otherwise it plays it's lowest card.

# Analysis #
When two random players compete, the average hand win is around 1.3 except for the leaders forehand which wins 8 on average. Each random player will make about 4.5 forehand errors and 5 backhand errors. When an otherwise random player simply bids as close as it can to those values, it makes only 1.4 errors in each hand. This means that, if you and your opponent are playing randomly, you will average 3 errors just with a fixed-bid strategy.

Two random players will tie 20% of the time. Two Agressive players will tie 7% of the time.

So far Agressive Player is the champion Tennis AI.
