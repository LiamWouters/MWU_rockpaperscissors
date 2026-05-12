import numpy as np
from algorithms.weighted_majority import WeightedMajority


def test_initial_weights():
    model = WeightedMajority(n_experts=2, alpha=0.5)

    np.testing.assert_allclose(model.raw_weights, [1.0, 1.0])
    np.testing.assert_allclose(model.probabilities, [0.5, 0.5])


def test_single_update():
    model = WeightedMajority(n_experts=2, alpha=0.5)

    # expert 0 correct, expert 1 wrong
    loss = np.array([0, 1])

    model.update(loss)

    expected_weights = np.array([1.0, 0.5])

    np.testing.assert_allclose(model.raw_weights, expected_weights)

    probs = model.probabilities
    assert np.isclose(np.sum(probs), 1.0)


def test_second_update_symmetry():
    model = WeightedMajority(n_experts=2, alpha=0.5)

    loss1 = np.array([0, 1])
    model.update(loss1)

    loss2 = np.array([1, 0])
    model.update(loss2)

    # both experts should now be equal again
    np.testing.assert_allclose(model.raw_weights, [0.5, 0.5])

    expert_predictions = np.array([1, 0])
    # equal weights: always predict 1
    pred = model.predict(expert_predictions)
    assert pred == 1


def test_prediction_majority_vote():
    model = WeightedMajority(n_experts=2, alpha=0.5)

    expert_predictions = np.array([0, 0])
    # 1 is never predicted, so always predict 0
    pred = model.predict(expert_predictions)
    assert pred == 0


def test_2_experts_20_iterations():
    iterations = 20
    alpha = 0.33
    decay = 1 - alpha
    n_experts = 2

    model = WeightedMajority(n_experts=n_experts, alpha=alpha)

    # First 19 rounds: all wrong
    for _ in range(iterations - 1):
        model.update(np.ones(n_experts))

    # Final round: only last expert is correct
    loss = np.ones(n_experts)
    loss[-1] = 0
    model.update(loss)

    # Expected weights
    expected_wrong = decay**iterations
    expected_right = decay ** (iterations - 1)

    np.testing.assert_allclose(
        model.raw_weights[:-1], np.full(n_experts - 1, expected_wrong)
    )

    np.testing.assert_allclose(model.raw_weights[-1], expected_right)

    # Prediction check
    expert_predictions = np.array([1] * 1 + [0] * 1)
    pred = model.predict(expert_predictions)

    assert pred == 0


def test_100_experts_1M_iterations():
    iterations = 1_000_000
    alpha = 0.1
    decay = 1 - alpha
    n_experts = 100

    model = WeightedMajority(n_experts=n_experts, alpha=alpha)

    # First 9999 rounds: all wrong
    for _ in range(iterations - 1):
        model.update(np.ones(n_experts))

    # Final round:
    # only last expert is correct
    loss = np.ones(n_experts)
    loss[-1] = 0
    model.update(loss)

    # Expected weights
    expected_wrong = decay**iterations
    expected_right = decay ** (iterations - 1)

    np.testing.assert_allclose(
        model.raw_weights[:-1], np.full(n_experts - 1, expected_wrong)
    )

    np.testing.assert_allclose(model.raw_weights[-1], expected_right)

    # Prediction check
    expert_predictions = np.array([0] * 50 + [1] * 50)
    pred = model.predict(expert_predictions)

    assert pred == 1
