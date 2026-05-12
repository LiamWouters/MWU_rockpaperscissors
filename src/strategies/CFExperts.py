import random
from enum import IntEnum

from game.util import COINFACE
from .AbstractStrategy import AbstractStrategy

class ConstantGuessExpert(AbstractStrategy):
    """
    Always guesses the same COINFACE
    """
    
    def __init__(self, always_guess: COINFACE):
        super().__init__(COINFACE)
        self.always_guess = always_guess
        self.name = f"{self.name}_{always_guess.name}"

    def play(self) -> COINFACE:
        return self.always_guess

    def update(self, outcome: COINFACE):
        pass

class GuessLastOutcomeExpert(AbstractStrategy):
    """
    First iteration: Random guess
    N'th iteration: outcome of last game
    """
    def __init__(self, seed=1):
        super().__init__(COINFACE)
        self._rng = random.Random(seed)
        self.last_outcome = self._rng.choice(list(self.options))
        
    def play(self) -> COINFACE:
        return self.last_outcome

    def update(self, outcome: COINFACE):
        self.last_outcome = outcome

class FrequencyGuessExpert(AbstractStrategy):
    """
    Keeps track of how many tails and heads have occurred and will make a weighted guess based on the frequencies
     - First iteration: random choice
    """
    def __init__(self, seed=1):
        super().__init__(COINFACE)
        self._rng = random.Random(seed)
        self.heads_count = 0
        self.tails_count = 0
        
    def play(self) -> COINFACE:
        if self.heads_count == 0 and self.tails_count == 0:
            return self._rng.choice(list(self.options))
        total = self.heads_count + self.tails_count
        weights = [
            self.tails_count/total, 
            self.heads_count/total
        ]
        return self._rng.choices(list(self.options), weights=weights)[0]

    def update(self, outcome: COINFACE):
        if outcome == COINFACE.HEADS:
            self.heads_count += 1
        elif outcome == COINFACE.TAILS:
            self.tails_count += 1
    
