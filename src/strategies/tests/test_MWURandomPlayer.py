import numpy as np

from algorithms import MWURegretTracker
from strategies import AbstractStrategy, MWURandomPlayer
from game import LossComputer
from game.util import COINFACE
from enum import IntEnum


class DummyExpert(AbstractStrategy):
    def __init__(self, fixed_move, options: IntEnum):
        super().__init__(options)
        self._move = fixed_move

    def play(self):
        return self._move

    def update(self, outcome):
        pass


class RandomCoinExpert(AbstractStrategy):
    def __init__(self, options: IntEnum, seed=None):
        super().__init__(options)
        self.rng = np.random.default_rng(seed)

    def play(self):
        return self.rng.choice([COINFACE.HEADS, COINFACE.TAILS])

    def update(self, outcome):
        pass


class DummyLoss(LossComputer):
    def compute_loss(self, move, outcome):
        return 0.0 if move == outcome else 1.0


def test_mwu_random_player_coin_game():
    experts = [
        DummyExpert(COINFACE.TAILS, options=COINFACE),  # always wrong
        DummyExpert(COINFACE.HEADS, options=COINFACE),  # always correct
    ]

    loss_fn = DummyLoss()

    alpha = 0.5
    player = MWURandomPlayer(
        experts=experts,
        loss_computer=loss_fn,
        moves_enum=COINFACE,
        alpha=0.5,
        seed=42,
        regret_tracker=MWURegretTracker(len(experts), alpha, max_t=200),
    )

    T = 200

    # training phase
    for t in range(T):
        player.play()
        player.update(COINFACE.HEADS)
        # after update
        print(f"Step {t + 1}")
        print("Cumulative loss per expert:", player.regret_tracker.cum_loss_experts)
        print("Learner cumulative loss:", player.regret_tracker.cum_loss_learner)
        print(
            "Learner cumulative expected loss:",
            player.regret_tracker.cum_expected_loss_learner,
        )

        print("Learner loss over time:", player.regret_tracker.history_learner)
        print(
            "Learner expected loss over time:",
            player.regret_tracker.history_learner_expected,
        )
        print("Best expert loss over time:", player.regret_tracker.history_best)
        print("Regret bound over time:", player.regret_tracker.history_bound)
        print("Expert losses over time:\n", player.regret_tracker.history_experts)
        print("\n")

    probs = player.probabilities

    # probability concentration
    assert probs[COINFACE.HEADS] > 0.95
    assert probs[COINFACE.TAILS] < 0.05
    assert np.isclose(np.sum(probs), 1.0)

    # behavioral test (sampling)
    n_samples = 200
    sampled_moves = []

    for _ in range(n_samples):
        move = player.play()
        sampled_moves.append(move)

    freq_heads = sampled_moves.count(COINFACE.HEADS) / n_samples

    # should strongly prefer HEADS
    assert freq_heads > 0.9


def test_mwu_fair_coin_game():
    rng = np.random.default_rng(42)

    loss_fn = DummyLoss()

    alphas = [1.0 * pow(10, -6), 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]

    T = 10_000

    for alpha in alphas:
        print(f"\nRunning alpha={alpha}")

        experts = []
        # build 100 random experts
        for i in range(100):
            experts.append(RandomCoinExpert(options=COINFACE, seed=i + 1))

        player = MWURandomPlayer(
            experts=experts,
            loss_computer=loss_fn,
            moves_enum=COINFACE,
            alpha=alpha,
            seed=42,
            regret_tracker=MWURegretTracker(len(experts), alpha, max_t=T),
        )

        # main loop
        for t in range(T):
            player.play()
            game_outcome = rng.choice([COINFACE.HEADS, COINFACE.TAILS])
            player.update(game_outcome)
            print(
                f"T={t+1}: Learner cumulative expected loss:",
                player.regret_tracker.cum_expected_loss_learner,
            )
