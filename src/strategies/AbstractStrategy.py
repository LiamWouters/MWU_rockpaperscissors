from abc import ABC, abstractmethod
from game import MOVES


class AbstractStrategy(ABC):

    @abstractmethod
    def play(self, gameHistory: list) -> MOVES:
        """
        Apply a strategy and return a move

        Arguments:
            - gameHistory: A chronological list of previous games
        """
        pass

    @abstractmethod
    def update(self, outcome: MOVES):
        """
        Update the strategy based on the observed outcome.

        Parameters
        ----------
        outcome : MOVES
            The observed result used to update the strategy.
        """
        pass
