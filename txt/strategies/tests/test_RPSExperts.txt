from game.util import MOVES
from strategies import (
    BeatLastHumanExpert,
    CopycatLastHumanExpert,
    FirstRandomThenFixedExpert,
    move_that_beats,
)


def test_first_random_then_fixed_repeats_first_move():
    expert = FirstRandomThenFixedExpert(seed=10)

    first = expert.play([])
    second = expert.play([])
    expert.update(MOVES.PAPER)
    third = expert.play([])

    assert first in list(MOVES)
    assert second == first
    assert third == first


def test_copycat_opens_random_then_copies_last_human_move():
    expert = CopycatLastHumanExpert(seed=20)

    opening = expert.play([])
    expert.update(MOVES.ROCK)
    second = expert.play([])
    expert.update(MOVES.SCISSORS)
    third = expert.play([])

    assert opening in list(MOVES)
    assert second == MOVES.ROCK
    assert third == MOVES.SCISSORS


def test_beat_last_human_plays_counter_move():
    expert = BeatLastHumanExpert(seed=30)

    opening = expert.play([])
    expert.update(MOVES.ROCK)
    second = expert.play([])
    expert.update(MOVES.PAPER)
    third = expert.play([])

    assert opening in list(MOVES)
    assert second == MOVES.PAPER
    assert third == MOVES.SCISSORS


def test_move_that_beats_respects_rps_rules():
    assert move_that_beats(MOVES.ROCK) == MOVES.PAPER
    assert move_that_beats(MOVES.PAPER) == MOVES.SCISSORS
    assert move_that_beats(MOVES.SCISSORS) == MOVES.ROCK
