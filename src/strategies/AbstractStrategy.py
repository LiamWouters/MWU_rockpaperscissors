from enum import IntEnum
from abc import ABC, abstractmethod
from game.util import MOVES, COINFACE

class AbstractStrategy(ABC):
    def __init__(self, options: IntEnum):
        """
        Arguments:
            - options: an IntEnum of all possible moves/options/choices
        """
        super().__init__()
        self.options = options 

    @abstractmethod
    def play(self, gameHistory: list) -> MOVES | COINFACE:
        """
        Apply a strategy and return a move

        Arguments:
            - gameHistory: A chronological list of previous games
        """
        pass

    @abstractmethod
    def update(self, outcome: MOVES | COINFACE):
        """
        Update the strategy based on the observed outcome.

        Parameters
        ----------
        outcome : MOVES or COINFACE
            The observed result used to update the strategy.
        """
        pass
