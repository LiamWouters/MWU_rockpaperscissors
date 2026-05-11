from typing import Optional
from enum import IntEnum

import numpy as np
from algorithms import WeightedMajority
from algorithms import WeightedMajorityRegretTracker
from game.util import MOVES
from game import LossComputer
from strategies import TrackedAbstractStrategy, AbstractStrategy


class WeightedMajorityPlayer(TrackedAbstractStrategy):
    """
    Player that plays using the Weighted Majority algorithm.

    Assumptions
    -----------
    - Exactly 2 possible moves
    - MOVES enum uses values {0, 1}
    """

    def __init__(
        self,
        experts: list[AbstractStrategy],
        loss_computer: LossComputer,
        moves_enum,
        alpha: float = 0.5,
        regret_tracker: Optional[WeightedMajorityRegretTracker] = None,
    ):
        super().__init__(moves_enum, regret_tracker)
        # binary action space
        assert len(moves_enum) == 2, "Only binary action spaces supported"
        values = {int(m) for m in moves_enum}
        assert values == {0, 1}, "MOVES must have values {0, 1}"

        # at least one expert
        assert len(experts) > 0, "At least one expert required"

        self._experts = tuple(experts)
        self._n_experts = len(experts)

        self._wm = WeightedMajority(n_experts=self._n_experts, alpha=alpha)
        self._loss_computer = loss_computer
        self._moves_enum = moves_enum

        self._last_expert_moves_int = None
        self._last_prediction_int = None

    def play(self) -> MOVES:
        """
        Returns a move using weighted majority vote over expert predictions.
        """
        expert_moves = [e.play() for e in self._experts]

        expert_moves_int = np.fromiter(
            (int(m) for m in expert_moves),
            dtype=int,
            count=self._n_experts,
        )
        self._last_expert_moves_int = expert_moves_int

        prediction_int = self._wm.predict(expert_moves_int)
        self._last_prediction_int = prediction_int

        return self._moves_enum(prediction_int)

    def update(self, outcome):
        """
        Updates expert weights based on observed outcome.
        Must be called after play().
        """

        if self._last_expert_moves_int is None:
            raise RuntimeError("update() called before play()")

        expert_losses = self._loss_computer.compute_losses(
            self._last_expert_moves_int,
            outcome,
        )

        self._wm.update(expert_losses)
        
        self.win_history.append(int(self._last_prediction_int == outcome))
        self.probability_history.append(self._wm.probabilities)

        learner_loss = self._loss_computer.compute_loss(
            self._last_prediction_int, outcome
        )

        if self._regret_tracker is not None:
            self._regret_tracker.update(
                loss_vector=expert_losses,
                learner_loss=learner_loss,
            )

        # prevents accidental reuse
        self._last_expert_moves_int = None
        self._last_prediction_int = None

        # update experts in case they adapt strategy
        for e in self._experts:
            e.update(outcome)

    @property
    def probabilities(self):
        return self._wm.probabilities

    @property
    def raw_weights(self):
        return self._wm.raw_weights

    @property
    def log_weights(self):
        return self._wm.log_weights

    @property
    def last_expert_moves(self):
        """
        Last expert predictions used in Weighted Majority update step.

        Returns
        -------
        list[MOVES] or None
            One move per expert from the last `play()` call.
        """
        return (
            None
            if self._last_expert_moves_int is None
            else [self._moves_enum(m) for m in self._last_expert_moves_int]
        )

    @property
    def regret_tracker(self) -> Optional[WeightedMajorityRegretTracker]:
        """Read-only access to regret tracker (may be None)."""
        return self._regret_tracker

    @property
    def experts(self):
        return self._experts

    @property
    def loss_computer(self):
        return self._loss_computer
