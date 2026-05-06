import random

from game.util import MOVES
from .AbstractStrategy import AbstractStrategy


def move_that_beats(move: MOVES) -> MOVES:
    move = MOVES(move)
    return MOVES((int(move) + 2) % 3)


class FirstRandomThenFixedExpert(AbstractStrategy):
    """
    Chooses one random RPS move on its first play, then repeats it forever.
    """

    def __init__(self, seed=1):
        super().__init__(MOVES)
        self._rng = random.Random(seed)
        self._fixed_move = None

    def play(self) -> MOVES:
        if self._fixed_move is None:
            self._fixed_move = self._rng.choice(list(MOVES))
        return self._fixed_move

    def update(self, outcome: MOVES):
        pass


class CopycatLastHumanExpert(AbstractStrategy):
    """
    Opens randomly, then copies the latest observed human move.
    """

    def __init__(self, seed=2):
        super().__init__(MOVES)
        self._rng = random.Random(seed)
        self._opening_move = None
        self._last_human_move = None

    def play(self) -> MOVES:
        if self._last_human_move is not None:
            return self._last_human_move

        if self._opening_move is None:
            self._opening_move = self._rng.choice(list(MOVES))
        return self._opening_move

    def update(self, outcome: MOVES):
        self._last_human_move = MOVES(outcome)


class BeatLastHumanExpert(AbstractStrategy):
    """
    Opens randomly, then plays the move that beats the latest human move.
    """

    def __init__(self, seed=3):
        super().__init__(MOVES)
        self._rng = random.Random(seed)
        self._opening_move = None
        self._last_human_move = None

    def play(self) -> MOVES:
        if self._last_human_move is not None:
            return move_that_beats(self._last_human_move)

        if self._opening_move is None:
            self._opening_move = self._rng.choice(list(MOVES))
        return self._opening_move

    def update(self, outcome: MOVES):
        self._last_human_move = MOVES(outcome)
