import json
import os
import re
from datetime import datetime
from typing import Callable, Iterable

from game.Loss import RPSLoss
from game.util import MOVES
from strategies.MWURandomPlayer import MWURandomPlayer


MOVE_ALIASES = {
    "0": MOVES.ROCK,
    "rock": MOVES.ROCK,
    "r": MOVES.ROCK,
    "1": MOVES.SCISSORS,
    "scissors": MOVES.SCISSORS,
    "scissor": MOVES.SCISSORS,
    "s": MOVES.SCISSORS,
    "2": MOVES.PAPER,
    "paper": MOVES.PAPER,
    "p": MOVES.PAPER,
}


def run_rps_auto_play(
    input_file_path: str,
    experts: dict,
    log_root_path: str | None = None,
    alpha: float = 0.5,
    seed: int = 42,
) -> dict:
    """
    Run auto Rock-Paper-Scissors from a predefined input file and write history.

    The input file is interpreted as the opponent/human moves. Tokens may be
    separated by commas, semicolons, whitespace, or newlines.
    """
    log_dir = _make_log_dir(log_root_path)
    history_path = os.path.join(log_dir, "history.json")
    expert_names, expert_list = _normalize_experts(experts)
    human_moves, parse_errors = parse_move_file(input_file_path, parse_rps_move)

    history = {
        "metadata": {
            "game": "Rock-Paper-Scissors",
            "mode": "auto",
            "algorithm": "mwu_random",
            "input_file": os.path.abspath(input_file_path),
            "log_dir": os.path.abspath(log_dir),
            "alpha": alpha,
            "seed": seed,
            "experts": expert_names,
            "total_input_moves": len(human_moves),
            "parse_errors": parse_errors,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
        "rounds": [],
        "summary": {
            "total_rounds": 0,
            "mwu_wins": 0,
            "human_wins": 0,
            "draws": 0,
            "cumulative_mwu_loss": 0.0,
            "cumulative_expert_losses": {name: 0.0 for name in expert_names},
        },
    }

    if not expert_list:
        history["metadata"]["error"] = "No experts configured."
        _write_json(history_path, history)
        return {"log_dir": log_dir, "history_path": history_path, "history": history}

    player = MWURandomPlayer(
        experts=expert_list,
        loss_computer=RPSLoss(),
        moves_enum=MOVES,
        alpha=alpha,
        seed=seed,
    )

    game_history = []
    for round_number, human_move in enumerate(human_moves, start=1):
        weights_before = _weights_snapshot(player)
        mwu_move = player.play(game_history)
        expert_moves = player.last_expert_moves or []
        selected_expert_index = player.last_expert_sampled
        selected_expert_name = expert_names[int(selected_expert_index)]

        expert_losses = player.loss_computer.compute_losses(expert_moves, human_move)
        learner_loss = player.loss_computer.compute_loss(mwu_move, human_move)
        result = _rps_result(mwu_move, human_move)

        player.update(human_move)
        weights_after = _weights_snapshot(player)

        for name, loss in zip(expert_names, expert_losses):
            history["summary"]["cumulative_expert_losses"][name] += float(loss)
        history["summary"]["cumulative_mwu_loss"] += float(learner_loss)
        _update_score(history["summary"], result)

        round_log = {
            "round": round_number,
            "human_move": _move_payload(human_move),
            "mwu_move": _move_payload(mwu_move),
            "selected_expert": {
                "index": int(selected_expert_index),
                "name": selected_expert_name,
            },
            "expert_moves": {
                name: _move_payload(move)
                for name, move in zip(expert_names, expert_moves)
            },
            "weights_before": weights_before,
            "weights_after": weights_after,
            "losses": {
                "mwu": float(learner_loss),
                "experts": {
                    name: float(loss)
                    for name, loss in zip(expert_names, expert_losses)
                },
            },
            "result": result,
            "cumulative": {
                "mwu_loss": history["summary"]["cumulative_mwu_loss"],
                "expert_losses": dict(history["summary"]["cumulative_expert_losses"]),
                "best_expert_loss": min(
                    history["summary"]["cumulative_expert_losses"].values()
                ),
                "regret_to_best_expert": history["summary"]["cumulative_mwu_loss"]
                - min(history["summary"]["cumulative_expert_losses"].values()),
            },
        }

        history["rounds"].append(round_log)
        game_history.append(round_log)

    history["summary"]["total_rounds"] = len(history["rounds"])
    _write_json(history_path, history)
    return {"log_dir": log_dir, "history_path": history_path, "history": history}


def parse_move_file(input_file_path: str, parse_move: Callable[[str], MOVES]) -> tuple[list[MOVES], list[dict]]:
    tokens = _read_move_tokens(input_file_path)
    moves = []
    errors = []

    for position, token in enumerate(tokens, start=1):
        try:
            moves.append(parse_move(token))
        except ValueError as exc:
            errors.append(
                {
                    "position": position,
                    "token": token,
                    "message": str(exc),
                }
            )

    return moves, errors


def parse_rps_move(token: str) -> MOVES:
    normalized = token.strip().lower()
    if normalized in MOVE_ALIASES:
        return MOVE_ALIASES[normalized]

    raise ValueError(
        "Expected one of ROCK/R, PAPER/P, SCISSORS/S, or enum values 0/1/2."
    )


def _read_move_tokens(input_file_path: str) -> list[str]:
    if not os.path.exists(input_file_path):
        return []

    with open(input_file_path, encoding="utf-8") as f:
        raw = f.read()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, list):
        return [str(item).strip() for item in _flatten(parsed) if str(item).strip()]

    tokens = []
    for line in raw.splitlines():
        line = line.split("#", 1)[0]
        tokens.extend(token for token in re.split(r"[\s,;]+", line) if token)
    return tokens


def _flatten(items: Iterable) -> Iterable:
    for item in items:
        if isinstance(item, list):
            yield from _flatten(item)
        else:
            yield item


def _normalize_experts(experts: dict) -> tuple[list[str], list]:
    if not experts:
        return [], []

    if isinstance(experts, dict):
        return [str(name) for name in experts.keys()], list(experts.values())

    expert_list = list(experts)
    return [f"expert_{index}" for index in range(len(expert_list))], expert_list


def _make_log_dir(log_root_path: str | None) -> str:
    log_root = log_root_path or os.path.join(os.getcwd(), "log")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_dir = os.path.join(log_root, f"log_{timestamp}")
    os.makedirs(log_dir, exist_ok=False)
    return log_dir


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _weights_snapshot(player: MWURandomPlayer) -> dict:
    return {
        "raw": _float_list(player.raw_weights),
        "log": _float_list(player.log_weights),
        "probabilities": _float_list(player.probabilities),
    }


def _float_list(values) -> list[float]:
    return [float(value) for value in values]


def _move_payload(move: MOVES) -> dict:
    move = MOVES(move)
    return {"name": move.name, "value": int(move)}


def _rps_result(mwu_move: MOVES, human_move: MOVES) -> str:
    loss = RPSLoss().compute_loss(mwu_move, human_move)
    if loss == 0.0:
        return "mwu_win"
    if loss == 0.5:
        return "draw"
    return "human_win"


def _update_score(summary: dict, result: str) -> None:
    if result == "mwu_win":
        summary["mwu_wins"] += 1
    elif result == "human_win":
        summary["human_wins"] += 1
    else:
        summary["draws"] += 1
