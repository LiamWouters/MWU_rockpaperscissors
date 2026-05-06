import os

from game.Loss import RPSLoss
from game.auto_play import parse_rps_move, run_rps_auto_play
from game.util import MOVES
from strategies import AbstractStrategy


class FixedExpert(AbstractStrategy):
    def __init__(self, move):
        self._move = move
        self.outcomes = []

    def play(self, gameHistory):
        return self._move

    def update(self, outcome):
        self.outcomes.append(outcome)


def test_rps_loss_uses_win_draw_loss_values():
    loss = RPSLoss()

    assert loss.compute_loss(MOVES.ROCK, MOVES.SCISSORS) == 0.0
    assert loss.compute_loss(MOVES.SCISSORS, MOVES.PAPER) == 0.0
    assert loss.compute_loss(MOVES.PAPER, MOVES.ROCK) == 0.0
    assert loss.compute_loss(MOVES.ROCK, MOVES.ROCK) == 0.5
    assert loss.compute_loss(MOVES.ROCK, MOVES.PAPER) == 1.0


def test_parse_rps_move_accepts_names_aliases_and_values():
    assert parse_rps_move("rock") == MOVES.ROCK
    assert parse_rps_move("R") == MOVES.ROCK
    assert parse_rps_move("paper") == MOVES.PAPER
    assert parse_rps_move("2") == MOVES.PAPER
    assert parse_rps_move("scissors") == MOVES.SCISSORS
    assert parse_rps_move("1") == MOVES.SCISSORS


def test_run_rps_auto_play_writes_traceable_history_json(tmp_path):
    input_path = tmp_path / "RPS_input.txt"
    input_path.write_text("rock, paper\nscissors\ninvalid\n", encoding="utf-8")

    result = run_rps_auto_play(
        input_file_path=str(input_path),
        experts={
            "rock_expert": FixedExpert(MOVES.ROCK),
            "paper_expert": FixedExpert(MOVES.PAPER),
        },
        log_root_path=str(tmp_path / "log"),
        seed=7,
    )

    history = result["history"]
    assert history["summary"]["total_rounds"] == 3
    assert len(history["metadata"]["parse_errors"]) == 1
    assert history["rounds"][0]["human_move"]["name"] == "ROCK"
    assert history["rounds"][0]["mwu_move"]["name"] in {"ROCK", "PAPER"}
    assert set(history["rounds"][0]["expert_moves"]) == {"rock_expert", "paper_expert"}
    assert "weights_before" in history["rounds"][0]
    assert "weights_after" in history["rounds"][0]
    assert "losses" in history["rounds"][0]
    assert "cumulative" in history["rounds"][-1]
    assert result["history_path"].endswith("history.json")
    assert os.path.exists(result["history_path"])
