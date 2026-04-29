from game.Moves import MOVES
from strategies import AbstractStrategy
import random

class RandomExpert(AbstractStrategy):
    def __init__(self, seed=1):
        random.seed(seed) # For reproducability
        super.__init__()
    
    def play(gameHistory: list):
        return random.choice(MOVES)
        