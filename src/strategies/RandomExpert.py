from enum import IntEnum
from game.util import MOVES
from strategies import AbstractStrategy
import random

class RandomExpert(AbstractStrategy):
    def __init__(self, options: IntEnum, seed=1):
        super().__init__(options)
        self._rng = random.Random(seed)  # For reproducibility

    def play(self):
        return self._rng.choice(list(self.options))

    def update(self, outcome: MOVES):
        pass
