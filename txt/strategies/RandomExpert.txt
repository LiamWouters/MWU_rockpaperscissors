from game.util import MOVES
from strategies import AbstractStrategy
import random


class RandomExpert(AbstractStrategy):
    def __init__(self, seed=1):
        self._rng = random.Random(seed)  # For reproducibility
        super().__init__()

    def play(self, gameHistory: list):
        return self._rng.choice(list(MOVES))

    def update(self, outcome: MOVES):
        pass
