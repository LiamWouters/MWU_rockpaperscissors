import numpy as np
from algorithms.regret_tracker import RegretTracker


class WeightedMajorityRegretTracker(RegretTracker):
    """
    Regret tracker for Weighted Majority Algorithm.
    """

    def __init__(self, n_experts, alpha, max_t):
        """
        Parameters
        ----------
        n_experts : int
            Number of experts.

        alpha : float
            Learning rate in (0, 1).

        max_t : int
            Maximum time horizon.
        """
        super().__init__(n_experts=n_experts, alpha=alpha, max_t=max_t)

    def _compute_bound(self, best_expert_loss):
        return (2 * np.log(self._n) / self._alpha) + 2 * (
            1 + self._alpha
        ) * best_expert_loss
