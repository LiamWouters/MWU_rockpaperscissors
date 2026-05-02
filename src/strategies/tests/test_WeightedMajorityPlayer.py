import numpy as np

from strategies import AbstractStrategy, WeightedMajorityPlayer
from algorithms import WeightedMajorityRegretTracker
from game import LossComputer


from enum import IntEnum


class CoinMove(IntEnum):
    TAILS = 0
    HEADS = 1


class DummyExpert(AbstractStrategy):
    def __init__(self, fixed_move):
        self._move = fixed_move

    def play(self, gameHistory):
        return self._move

    def update(self, outcome):
        pass


class DummyLoss(LossComputer):
    def compute_loss(self, move, outcome):
        return 0.0 if move == outcome else 1.0


def test_weighted_majority_player_coin_game():
    experts = [
        DummyExpert(CoinMove.TAILS),
        DummyExpert(CoinMove.HEADS),
    ]

    loss_fn = DummyLoss()

    alpha = 0.5
    T = 50

    player = WeightedMajorityPlayer(
        experts=experts,
        loss_computer=loss_fn,
        moves_enum=CoinMove,
        alpha=alpha,
        regret_tracker=WeightedMajorityRegretTracker(len(experts), alpha, max_t=50),
    )

    for t in range(T):
        move = player.play([])
        if t >= 1:
            assert move == CoinMove.HEADS
        player.update(CoinMove.HEADS)

        # after update
        print(f"Step {t + 1}")
        print("Cumulative loss per expert:", player.regret_tracker.cum_loss_experts)
        print("Learner cumulative loss:", player.regret_tracker.cum_loss_learner)

        print("Learner loss over time:", player.regret_tracker.history_learner)
        print("Best expert loss over time:", player.regret_tracker.history_best)
        print("Regret bound over time:", player.regret_tracker.history_bound)
        print("Expert losses over time:\n", player.regret_tracker.history_experts)
        print("\n")

    probs = player.probabilities

    assert probs[1] > 0.999
    assert probs[0] < 0.001
    assert np.isclose(np.sum(probs), 1.0)
