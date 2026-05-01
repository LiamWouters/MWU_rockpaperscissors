import numpy as np
from scipy.special import softmax


class MultiplicativeWeightsRandom:
    """
    Multiplicative Weights Update Algorithm with stochastic expert sampling.

    Parameters
    ----------
    n_experts : int
        Number of experts (must be ≥ 1).

    alpha : float, default=0.5
        Learning rate controlling weight decay:
        - small alpha: slow adaptation
        - large alpha: fast penalization of errors

        Must satisfy 0 < alpha < 1.
    """

    def __init__(self, n_experts, alpha=0.5):
        assert n_experts >= 1, "Number of experts must be at least 1"
        assert 0 < alpha < 1, "alpha must be in the open interval (0, 1)"

        self._alpha = alpha
        self._log_decay = np.log(1 - alpha)
        self._n = n_experts

        # log(w_i) = 0  <=> w_i = 1
        self._log_weights = np.zeros(n_experts)
        # initialize probabilities
        self._update_probabilities()

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
        Returns probability distribution over experts.

        Returns
        -------
        np.ndarray of shape (n_experts,)
            Probability distribution over experts.
        """
        return self._probs.copy()

    def sample_expert(self):
        """
        Samples an expert according to the current probability distribution.

        Returns
        -------
        int
            Index of the selected expert.
        """
        return np.random.choice(self._n, p=self._probs)

    def expected_loss(self, loss_vector):
        """
        Computes expected loss under the current expert distribution.

        Parameters
        ----------
        loss_vector : array-like of shape (n_experts,)
            Loss value for each expert (must be in [0, 1]).

        Returns
        -------
        float
            Expected loss under the current probabilities.
        """
        loss_vector = self._validate_loss_vector(loss_vector)
        return np.dot(self._probs, loss_vector)

    def update(self, loss_vector):
        """
        Updates expert weights using multiplicative weight update rule.

        Each expert weight is scaled by:
            w_i ← w_i * (1 - alpha)^{loss_i}

        Implemented in log-space for numerical stability:
            log w_i ← log w_i + loss_i * log(1 - alpha)

        Parameters
        ----------
        loss_vector : array-like of shape (n_experts,)
            Loss per expert in [0, 1], where 0 = best, 1 = worst.
        """
        loss_vector = self._validate_loss_vector(loss_vector)
        self._log_weights += loss_vector * self._log_decay
        # recompute probabilities
        self._update_probabilities()

    def _update_probabilities(self):
        self._probs = softmax(self._log_weights)
        assert np.isclose(np.sum(self._probs), 1.0), "Probabilities not normalized"

    def _validate_loss_vector(self, loss_vector):
        loss_vector = np.asarray(loss_vector)

        assert loss_vector.shape == (
            self._n,
        ), f"Loss vector shape does not match number of experts ({self._n})"

        assert np.all(
            (0.0 <= loss_vector) & (loss_vector <= 1.0)
        ), "Loss values must be in closed interval [0, 1]"

        return loss_vector
