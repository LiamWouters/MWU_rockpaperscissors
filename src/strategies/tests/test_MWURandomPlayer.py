import numpy as np

from strategies import AbstractStrategy, MWURandomPlayer
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


def test_mwu_random_player_concentrates_on_best_expert():
    experts = [
        DummyExpert(CoinMove.TAILS),  # always wrong
        DummyExpert(CoinMove.HEADS),  # always correct
    ]

    loss_fn = DummyLoss()

    player = MWURandomPlayer(
        experts=experts,
        loss_computer=loss_fn,
        moves_enum=CoinMove,
        alpha=0.5,
        seed=42,
    )

    T = 200

    # training phase
    for _ in range(T):
        player.play([])
        player.update(CoinMove.HEADS)

    probs = player.probabilities

    # probability concentration
    assert probs[CoinMove.HEADS] > 0.95
    assert probs[CoinMove.TAILS] < 0.05
    assert np.isclose(np.sum(probs), 1.0)

    # behavioral test (sampling)
    n_samples = 200
    sampled_moves = []

    for _ in range(n_samples):
        move = player.play([])
        sampled_moves.append(move)

    freq_heads = sampled_moves.count(CoinMove.HEADS) / n_samples

    # should strongly prefer HEADS
    assert freq_heads > 0.9
