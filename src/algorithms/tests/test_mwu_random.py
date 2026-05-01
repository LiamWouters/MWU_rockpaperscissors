import numpy as np
from algorithms.mwu_random import MultiplicativeWeightsRandom


def test_initial_probabilities():
    model = MultiplicativeWeightsRandom(n_experts=2, alpha=0.5)

    np.testing.assert_allclose(model.probabilities, [0.5, 0.5])
    np.testing.assert_allclose(model.raw_weights, [1.0, 1.0])


def test_single_update():
    model = MultiplicativeWeightsRandom(n_experts=2, alpha=0.5)

    loss = np.array([0, 1])  # expert 1 wrong
    model.update(loss)

    # weights: [1, 0.5]
    np.testing.assert_allclose(model.raw_weights, [1.0, 0.5])

    # probabilities
    probs = model.probabilities
    np.testing.assert_allclose(probs, [2 / 3, 1 / 3])

    assert np.isclose(np.sum(probs), 1.0)


def test_second_update_symmetry():
    model = MultiplicativeWeightsRandom(n_experts=2, alpha=0.5)

    model.update([0, 1])
    model.update([0, 1])

    np.testing.assert_allclose(model.raw_weights, [1.0, 0.25])


def test_prediction_sampling():
    model = MultiplicativeWeightsRandom(n_experts=2, alpha=0.5)

    model.update([1, 0])
    model.update([1, 0])
    model.update([1, 0])

    pred = model.sample_expert()

    assert pred in [0, 1]


def test_20_iterations():
    model = MultiplicativeWeightsRandom(n_experts=2, alpha=0.1)

    decay = 0.9
    T = 20

    for _ in range(T - 1):
        model.update(np.array([1, 1]))

    model.update(np.array([0, 1]))

    expected_weights = np.array([decay ** (T - 1), decay**T])
    expected_probs = expected_weights / np.sum(expected_weights)

    np.testing.assert_allclose(model.raw_weights, expected_weights)
    np.testing.assert_allclose(model.probabilities, expected_probs, rtol=1e-8)


def test_rps_3_experts_5_iterations():
    n_experts = 3
    T = 5
    alpha = 0.1
    decay = 1 - alpha

    model = MultiplicativeWeightsRandom(n_experts=n_experts, alpha=alpha)

    # first wins, second ties, third loses
    loss_vec = np.array([0.0, 0.5, 1.0])

    for _ in range(T):
        model.update(loss_vec)

    raw = model.raw_weights
    probs = model.probabilities

    # expert 0 (winner)
    exp0 = 1.0

    # expert 1 (tie)
    exp1 = (decay**0.5) ** T

    # expert 2 (loser)
    exp2 = (decay**1) ** T

    expected_raw = np.array(
        [
            exp0,
            exp1,
            exp2,
        ]
    )
    expected_probs = expected_raw / np.sum(expected_raw)

    np.testing.assert_allclose(raw, expected_raw, rtol=1e-8)

    assert np.isclose(np.sum(probs), 1.0)

    np.testing.assert_allclose(probs, expected_probs, rtol=1e-8)

    # winner should dominate
    assert np.argmax(probs) == 0


def test_2_experts_1M_iterations():
    n_experts = 2
    T = 1_000_000
    alpha = 0.1

    model = MultiplicativeWeightsRandom(n_experts=n_experts, alpha=alpha)

    # loss definitions
    loss_vec = np.array([0.33, 0.33])

    # first T-1 rounds: tied losses
    for _ in range(T - 1):
        model.update(loss_vec)

    # final round, only second one loses
    model.update([0.0, 0.33])
    probs = model.probabilities

    # winner should dominate
    assert np.argmax(probs) == 0
