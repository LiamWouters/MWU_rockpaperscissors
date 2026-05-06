import numpy as np
from abc import ABC, abstractmethod


class RegretTracker(ABC):
    """
    Abstract base class for regret tracking algorithms.
    """

    def __init__(self, n_experts, alpha, max_t, use_expected_loss: bool = False):
        self._n = n_experts
        self._alpha = alpha
        self._max_t = max_t - 1
        self._t = 0

        self._cum_loss_experts = np.zeros(n_experts)
        self._cum_loss_learner = 0.0

        self._history_learner = np.zeros(max_t)
        self._history_best = np.zeros(max_t)
        self._history_bound = np.zeros(max_t)
        self._history_experts = np.zeros((max_t, n_experts))

        # in case we need to track expected loss
        self._use_expected_loss = use_expected_loss
        if use_expected_loss:
            self._cum_expected_loss_learner = 0.0
            self._history_cum_expected_loss_learner = np.zeros(max_t)

    def update(self, loss_vector, learner_loss, expected_learner_loss=None):
        loss_vector = np.asarray(loss_vector)

        if self._t > self._max_t:
            raise RuntimeError("Maximum time horizon exceeded")

        self._cum_loss_experts += loss_vector
        self._cum_loss_learner += learner_loss

        best_expert_loss = np.min(self._cum_loss_experts)

        bound = self._compute_bound(best_expert_loss)

        if self._use_expected_loss:
            assert expected_learner_loss is not None
            self._cum_expected_loss_learner += expected_learner_loss
            self._history_cum_expected_loss_learner[self._t] = (
                self._cum_expected_loss_learner
            )
            assert self._cum_expected_loss_learner <= bound + 1e-9, (
                f"Bound violated at t={self._t}: "
                f"E(L_learner)={self._cum_expected_loss_learner}, bound={bound}"
            )
        else:
            assert self._cum_loss_learner <= bound + 1e-9, (
                f"Bound violated at t={self._t}: "
                f"L_learner={self._cum_loss_learner}, bound={bound}"
            )

        self._history_learner[self._t] = self._cum_loss_learner
        self._history_best[self._t] = best_expert_loss
        self._history_bound[self._t] = bound
        self._history_experts[self._t] = self._cum_loss_experts

        self._t += 1

    @abstractmethod
    def _compute_bound(self, best_expert_loss):
        """Compute regret bound (implemented by subclasses)."""
        pass

    @property
    def t(self):
        """Current time step (number of updates performed)."""
        return self._t

    @property
    def n_experts(self):
        """Number of experts."""
        return self._n

    @property
    def alpha(self):
        """Learning rate parameter."""
        return self._alpha

    @property
    def cum_loss_experts(self):
        """Current cumulative loss per expert.

        Returns
        -------
        np.ndarray of shape (n_experts,)
        """
        return self._cum_loss_experts.copy()

    @property
    def cum_loss_learner(self):
        """Current cumulative loss of the learner.

        Returns
        -------
        float
        """
        return self._cum_loss_learner

    @property
    def cum_expected_loss_learner(self):
        """Current cumulative loss of the learner.

        Returns
        -------
        float
        """
        if self._use_expected_loss:
            return self._cum_expected_loss_learner
        return self._cum_loss_learner

    @property
    def history_learner(self):
        """Learner cumulative loss over time.

        Returns
        -------
        np.ndarray of shape (t,)
        """
        return self._history_learner[: self._t]

    @property
    def history_learner_expected(self):
        """Learner cumulative expected loss over time.

        Returns
        -------
        np.ndarray of shape (t,)
        """
        if self._use_expected_loss:
            return self._history_cum_expected_loss_learner[: self._t]
        else:
            return self._history_learner[: self._t]

    @property
    def history_best(self):
        """Best expert cumulative loss over time.

        Returns
        -------
        np.ndarray of shape (t,)
        """
        return self._history_best[: self._t]

    @property
    def history_bound(self):
        """Regret bound over time.

        Returns
        -------
        np.ndarray of shape (t,)
        """
        return self._history_bound[: self._t]

    @property
    def history_experts(self):
        """Cumulative loss per expert over time.

        Returns
        -------
        np.ndarray of shape (t, n_experts)
        """
        return self._history_experts[: self._t]
