from typing import Optional
from enum import IntEnum

import numpy as np
from algorithms import MultiplicativeWeightsRandom
from algorithms import MWURegretTracker
from game.util import MOVES
from game import LossComputer
from strategies import AbstractStrategy


class MWURandomPlayer(AbstractStrategy):
    """
    Player that uses Multiplicative Weights with randomized expert sampling.
    """

    def __init__(
        self,
        experts: list[AbstractStrategy],
        loss_computer: LossComputer,
        moves_enum,
        alpha: float = 0.5,
        regret_tracker: Optional[MWURegretTracker] = None,
        seed: int = 42,
    ):
        super().__init__(moves_enum)
        assert len(experts) > 0, "At least one expert required"

        self._experts = tuple(experts)
        self._n_experts = len(experts)

        self._mwu = MultiplicativeWeightsRandom(
            n_experts=self._n_experts,
            alpha=alpha,
            seed=seed,
        )

        self._loss_computer = loss_computer
        self._moves_enum = moves_enum
        self._regret_tracker = regret_tracker

        self._last_expert_moves_int = None
        self._last_prediction_int = None
        self._last_expert_sampled_int = None

    def play(self) -> MOVES:
        """
        Samples a move using MWU-weighted random expert selection.
        """
        expert_moves = [e.play() for e in self._experts]

        expert_moves_int = np.fromiter(
            (int(m) for m in expert_moves),
            dtype=int,
            count=self._n_experts,
        )

        self._last_expert_moves_int = expert_moves_int

        sampled_expert = self._mwu.sample_expert()
        self._last_expert_sampled_int = sampled_expert

        prediction_int = expert_moves_int[sampled_expert]
        self._last_prediction_int = prediction_int

        return self._moves_enum(prediction_int)

    # --------------------------------------------------
    # learning
    # --------------------------------------------------
    def update(self, outcome):
        """
        Updates MWU weights and (optionally) regret tracker.
        Must be called after play().
        """

        if self._last_expert_moves_int is None:
            raise RuntimeError("update() called before play()")

        expert_losses = self._loss_computer.compute_losses(
            self._last_expert_moves_int,
            outcome,
        )

        self._mwu.update(expert_losses)

        learner_loss = self._loss_computer.compute_loss(
            self._last_prediction_int,
            outcome,
        )

        if self._regret_tracker is not None:
            self._regret_tracker.update(
                loss_vector=expert_losses,
                learner_loss=learner_loss,
            )

        self._last_expert_moves_int = None
        self._last_prediction_int = None
        self._last_expert_sampled_int = None

        for e in self._experts:
            e.update(outcome)

    @property
    def probabilities(self):
        return self._mwu.probabilities

    @property
    def raw_weights(self):
        return self._mwu.raw_weights

    @property
    def log_weights(self):
        return self._mwu.log_weights

    @property
    def regret_tracker(self) -> Optional[MWURegretTracker]:
        """Read-only access to regret tracker (may be None)."""
        return self._regret_tracker

    @property
    def last_expert_moves(self):
        """
        Last expert predictions used in MWU update step.

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
    def last_expert_sampled(self):
        """
        Index of last expert sampled for play().

        Returns
        -------
        int or None
            Index of last expert sampled for play().
        """
        return self._last_expert_sampled_int

    @property
    def experts(self):
        return self._experts

    @property
    def loss_computer(self):
        return self._loss_computer
