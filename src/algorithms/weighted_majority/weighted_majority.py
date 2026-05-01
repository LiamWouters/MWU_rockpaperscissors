import numpy as np
from scipy.special import softmax, logsumexp


class WeightedMajority:
    """
    Deterministic Weighted Majority Algorithm.

    Parameters
    ----------
    n_experts : int
        Number of experts (must be ≥ 1).

    alpha : float, default=0.5
        Learning rate controlling weight decay:
        - small alpha: slow adaptation
        - large alpha: fast penalization of errors

        Must satisfy 0 < alpha <= 0.5.
    """

    def __init__(self, n_experts, alpha=0.5):
        assert n_experts >= 1, "Number of experts must be at least 1"
        assert 0 < alpha <= 0.5, "alpha must be in (0, 1/2]"

        self._n = n_experts
        self._alpha = alpha

        # log-weights instead of raw weights
        self._log_weights = np.zeros(n_experts)
        self._log_decay = np.log(1 - self._alpha)

    # -----------------------------
    # properties
    # -----------------------------
    @property
    def alpha(self):
        return self._alpha

    @property
    def n_experts(self):
        return self._n

    @property
    def log_weights(self):
        """
        Returns the internal log-weights of the experts.
        These are maintained for numerical stability during updates.

        Returns
        -------
        np.ndarray of shape (n_experts,)
            Logarithm of expert weights.
        """
        return self._log_weights

    @property
    def raw_weights(self):
        """
        Returns the weights of the experts.

        Returns
        -------
        np.ndarray of shape (n_experts,)
            Expert weights.
        """
        return np.exp(self._log_weights)

    @property
    def probabilities(self):
        """
        Returns the normalized weights over experts.

        Returns
        -------
        np.ndarray of shape (n_experts,)
            Normalized expert weights.
        """
        return softmax(self._log_weights)

    def predict(self, expert_predictions):
        """
        Predicts 0 or 1 using a weighted majority vote.

        Parameters
        ----------
        expert_predictions : array-like of shape (n_experts,)
            Binary predictions from each expert (0 or 1).

        Returns
        -------
        int
            Predicted class (0 or 1).
        """
        expert_predictions = self._validate_vector(expert_predictions)

        mask_0 = expert_predictions == 0
        mask_1 = expert_predictions == 1

        log_weight_0 = (
            logsumexp(self._log_weights[mask_0]) if np.any(mask_0) else -np.inf
        )
        log_weight_1 = (
            logsumexp(self._log_weights[mask_1]) if np.any(mask_1) else -np.inf
        )

        return 1 if log_weight_1 >= log_weight_0 else 0

    def update(self, loss_vector):
        """
        Updates expert weights using the weighted majority update rule.

        Experts with loss loss_i are penalized by multiplying their weight by (1 - alpha)^loss_i:
            log w_i ← log w_i + loss_i * log(1 - alpha)

        Parameters
        ----------
        loss_vector : array-like of shape (n_experts,)
            Binary loss per expert (0 = correct, 1 = wrong).
        """
        loss_vector = self._validate_vector(loss_vector)
        self._log_weights += loss_vector * self._log_decay

    def _validate_vector(self, v):
        v = np.asarray(v)

        assert v.shape == (self._n,), f"Vector shape must be ({self._n},)"

        assert np.all(
            np.isin(v, [0, 1])
        ), "Values must be binary: 0 (correct), 1 (wrong)"

        return v
