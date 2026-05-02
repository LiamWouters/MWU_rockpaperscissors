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


def test_mwu_player_exact_convergence_coin_game():
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
        regret_tracker=WeightedMajorityRegretTracker(len(experts), alpha, max_t=100),
    )

    for i in range(T):
        move = player.play([])
        if i >= 1:
            assert move == CoinMove.HEADS
        player.update(CoinMove.HEADS)

    probs = player.probabilities

    assert probs[1] > 0.999
    assert probs[0] < 0.001
    assert np.isclose(np.sum(probs), 1.0)
