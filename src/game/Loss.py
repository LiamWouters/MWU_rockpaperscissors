from abc import ABC, abstractmethod

import numpy as np
from game.util import MOVES, COINFACE

class LossComputer(ABC):

    @abstractmethod
    def compute_loss(self, move: MOVES, outcome: MOVES) -> float:
        """
        Compute the loss for a given move and the game outcome.

        Parameters
        ----------
        move : Move made by the player or expert
        outcome: The outcome of the game

        Returns
        -------
        float
            Loss for the given move and game outcome.
        """
        pass

    def compute_losses(self, moves: list[MOVES], outcome: MOVES) -> np.ndarray:
        """
        Compute the losses for a list of moves and the game outcome.

        Parameters
        ----------
        moves : list of MOVES
        outcome: The outcome of the game

        Returns
        -------
        np.ndarray of shape (len(moves),)
            Loss for each move.
        """
        return np.array([self.compute_loss(m, outcome) for m in moves])


class RPSLoss(LossComputer):
    def compute_loss(self, move: MOVES, outcome: MOVES) -> float:
        """
        Compute the loss for a given move.
        Returns:
            0 if the player wins
            0.5 if the player draws
            1 if the player loses

        Arguments:
            - move: The move made by the player or expert
        """
        move = MOVES(move)
        outcome = MOVES(outcome)

        if move == outcome:
            return 0.5

        # With the current enum values:
        # ROCK=0 beats SCISSORS=1, SCISSORS=1 beats PAPER=2,
        # and PAPER=2 beats ROCK=0.
        return 0.0 if (move - outcome) % 3 == 2 else 1.0

class CFLoss(LossComputer):
    def compute_loss(self, move: COINFACE, outcome: COINFACE) -> float:
        """
        Compute the loss for a given move. (move = prediction)
        Returns:
            0 if the player wins, prediction was correct
            1 if the player loses, prediction was wrong

        Arguments:
            - move: The move made by the player or expert
        """
        return 0.0 if (move == outcome) else 1.0
