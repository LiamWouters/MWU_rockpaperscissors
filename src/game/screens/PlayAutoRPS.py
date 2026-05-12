import copy
import json
import os
from datetime import datetime

import pygame

from algorithms import MWURegretTracker
from game import RPSLoss
from game.auto_play import parse_move_file, parse_rps_move
from game.util import (
    GAMESTATE,
    GAMES,
    MOVES,
    Button,
    FileView,
    ImageView,
    NumberInput,
    TextLabel,
    Switch,
    get_font,
)
from strategies import MWURandomPlayer
from strategies.RandomExpert import RandomExpert
from .GameScreen import *

RPS_INPUT_FILE_PATH = os.path.join(os.getcwd(), "RPS_input.txt")
RPS_AUTO_HISTORY_DISPLAY_FILE_PATH = os.path.join(os.getcwd(), "RPS_auto_history.txt")
RPS_AUTO_EXPERT_STATS_FILE_PATH = os.path.join(os.getcwd(), "RPS_auto_expert_stats.txt")
HISTORY_DISPLAY_LIMIT = 10


class PlayAutoRPS(GameScreen):
    def __init__(self, screen, experts=None):
        super().__init__(screen)
        self.experts = experts or {"random": RandomExpert(MOVES)}
        self.expert_names = [str(name) for name in self.experts.keys()]
        self.alpha = 0.5
        self.max_time_horizon = 200
        self.show_graph_weights = True
        self.show_graph_bound = True
        self.show_graph_expected = True
        self.limit_graph_timesteps = 0
        self._has_run = False
        self._last_result = None

        open(RPS_INPUT_FILE_PATH, "a", encoding="utf-8").close()
        open(RPS_AUTO_HISTORY_DISPLAY_FILE_PATH, "w", encoding="utf-8").close()
        open(RPS_AUTO_EXPERT_STATS_FILE_PATH, "w", encoding="utf-8").close()

        self.elements["TITLE_TEXT"] = get_font(34).render(
            f"Auto Play {GAMES.RPS.value}", True, white
        )
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 16)
        )
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="<- BACK",
        )
        self.elements["HISTORY_VIEW"] = FileView(
            pos=(self.screen.get_width() * 14 / 100, self.screen.get_height() * 53 / 100),
            size=(self.screen.get_width() * 22 / 100, self.screen.get_height() * 70 / 100),
            font=get_font(12),
            file_path=RPS_AUTO_HISTORY_DISPLAY_FILE_PATH,
            preamble="LAST 10 AUTO ROUNDS:",
            show_bounding_box=True,
        )
        self.elements["ALPHA_INPUT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 15 / 100),
            font=get_font(16),
            text="Set Alpha (LR):",
        )
        self.elements["ALPHA_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 18 / 100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_alpha,
            start_value=self.alpha,
            start_text="alpha",
            lowerLimit=0,
            upperLimit=0.5,
        )
        self.elements["MAX_T_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 22 / 100),
            font=get_font(16),
            text="Set max time horizon:",
        )
        self.elements["MAX_T_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 25 / 100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_max_time_horizon,
            start_value=self.max_time_horizon,
            start_text="time horizon",
            lowerLimit=1,
        )
        self.elements["RUN_BUTTON"] = Button(
            pos=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 35 / 100),
            font=get_font(28),
            text="RUN AUTO",
            show_bounding_box=True,
        )
        self.elements["STATUS_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 41 / 100, self.screen.get_height() * 45 / 100),
            font=get_font(16),
            text="Preparing auto run...",
        )
        self.elements["SCORE_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 41 / 100, self.screen.get_height() * 52 / 100),
            font=get_font(16),
            text="Score: MWU 0 | Input 0 | Draws 0",
        )
        self.elements["ROUND_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 41 / 100, self.screen.get_height() * 57 / 100),
            font=get_font(16),
            text="Total Rounds: 0",
        )
        self.elements["LOG_PATH_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 41 / 100, self.screen.get_height() * 62 / 100),
            font=get_font(12),
            text="Log:",
        )
        self.elements["EXPERT_STATS_VIEW"] = FileView(
            pos=(self.screen.get_width() * 41 / 100, self.screen.get_height() * 80 / 100),
            size=(self.screen.get_width() * 34 / 100, self.screen.get_height() * 22 / 100),
            font=get_font(12),
            file_path=RPS_AUTO_EXPERT_STATS_FILE_PATH,
            preamble="EXPERT RANKING:",
            show_bounding_box=True,
        )

        self.elements["GRAPH_VIEW"] = ImageView(
            pos=(self.screen.get_width() * 78 / 100, self.screen.get_height() * 46 / 100),
            image=None,
            show_bounding_box=False,
        )
        self.elements["GRAPH_LIMIT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 62 / 100, self.screen.get_height() * 87 / 100),
            font=get_font(16),
            text="Set timestep limit:",
        )
        self.elements["GRAPH_LIMIT_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 62 / 100, self.screen.get_height() * 90 / 100),
            font=get_font(16),
            fixed_width=100,
            callback=self._set_timestep_limit,
            start_value=self.limit_graph_timesteps,
            start_text="timestep limit",
            lowerLimit=-1,
        )
        self.elements["GRAPH_EXPECTED_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 83 / 100, self.screen.get_height() * 87 / 100),
            font=get_font(16),
            slider_size=(35, 20),
            option1text="Hide expected loss",
        )
        self.elements["GRAPH_BOUND_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 83 / 100, self.screen.get_height() * 90 / 100),
            font=get_font(16),
            slider_size=(35, 20),
            option1text="Hide bound",
        )
        self.elements["GRAPH_WEIGHTS_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 83 / 100, self.screen.get_height() * 93 / 100),
            font=get_font(16),
            slider_size=(35, 20),
            option1text="Hide weights",
        )

        self._reset_state()

    def _draw(self):
        self._ensure_auto_play_ran()
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])

        new_surface = self.MWU.get_new_graph_surface()
        if new_surface is not None:
            self.elements["GRAPH_VIEW"].set_image(new_surface)

    def _handle_events(self, events):
        for event in events:
            self.elements["ALPHA_INPUT"].handleEvent(event)
            self.elements["MAX_T_INPUT"].handleEvent(event)
            self.elements["GRAPH_LIMIT_INPUT"].handleEvent(event)
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    self.reset()
                    return GAMESTATE.MENU
                elif self.elements["ALPHA_INPUT"].is_hovered():
                    self.elements["ALPHA_INPUT"].toggleSelected()
                elif self.elements["MAX_T_INPUT"].is_hovered():
                    self.elements["MAX_T_INPUT"].toggleSelected()
                elif self.elements["RUN_BUTTON"].is_hovered():
                    self.reset()
                elif self.elements["GRAPH_LIMIT_INPUT"].is_hovered():
                    self.elements["GRAPH_LIMIT_INPUT"].toggleSelected()
                elif self.elements["GRAPH_EXPECTED_TOGGLE"].is_hovered():
                    self.elements["GRAPH_EXPECTED_TOGGLE"].switch()
                    self.show_graph_expected = not self.elements["GRAPH_EXPECTED_TOGGLE"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_BOUND_TOGGLE"].is_hovered():
                    self.elements["GRAPH_BOUND_TOGGLE"].switch()
                    self.show_graph_bound = not self.elements["GRAPH_BOUND_TOGGLE"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_WEIGHTS_TOGGLE"].is_hovered():
                    self.elements["GRAPH_WEIGHTS_TOGGLE"].switch()
                    self.show_graph_weights = not self.elements["GRAPH_WEIGHTS_TOGGLE"].state
                    self._draw_current_graph()

    def reset(self):
        self._has_run = False
        self._reset_state()

    def _set_alpha(self, value):
        if self.alpha == value:
            return
        self.alpha = value
        self.reset()

    def _set_max_time_horizon(self, value):
        if self.max_time_horizon == value:
            return
        self.max_time_horizon = int(value)
        self.reset()

    def _set_timestep_limit(self, value):
        self.limit_graph_timesteps = int(value)
        self._draw_current_graph()

    def _ensure_auto_play_ran(self):
        if self._has_run:
            return
        self._has_run = True
        self._run_auto_play()

    def _reset_state(self):
        self.total_rounds = 0
        self.parse_errors = []
        self.log_dir = None
        self.history_path = None
        self.MWU = MWURandomPlayer(
            experts=copy.deepcopy(list(self.experts.values())),
            loss_computer=RPSLoss(),
            moves_enum=MOVES,
            alpha=self.alpha,
            regret_tracker=MWURegretTracker(
                len(self.experts), self.alpha, max_t=self.max_time_horizon
            ),
            seed=42,
        )
        self.history = self._new_history()
        self._write_history_display()
        self._write_expert_stats_display()
        self.elements["STATUS_TEXT"].updateText("Preparing auto run...")
        self.elements["SCORE_TEXT"].updateText("Score: MWU 0 | Input 0 | Draws 0")
        self.elements["ROUND_TEXT"].updateText("Total Rounds: 0")
        self.elements["LOG_PATH_TEXT"].updateText("Log:")
        self.elements["GRAPH_VIEW"].clear()

    def _run_auto_play(self):
        human_moves, parse_errors = parse_move_file(RPS_INPUT_FILE_PATH, parse_rps_move)
        self.parse_errors = parse_errors
        self.history["metadata"]["total_input_moves"] = len(human_moves)
        self.history["metadata"]["parse_errors"] = parse_errors

        if not human_moves:
            self._finish_run("No valid moves found in RPS_input.txt.")
            return

        moves_to_play = human_moves[: self.max_time_horizon]
        for human_move in moves_to_play:
            self._play_round(human_move)

        status = f"Auto run complete: {self.total_rounds} rounds"
        if len(human_moves) > self.total_rounds:
            status += f" ({len(human_moves) - self.total_rounds} beyond max horizon skipped)"
        if parse_errors:
            status += f" ({len(parse_errors)} invalid tokens skipped)"
        self._finish_run(status)
        self._draw_current_graph()

    def _play_round(self, human_move: MOVES):
        round_number = self.total_rounds + 1
        weights_before = self._weights_snapshot()
        mwu_move = self.MWU.play()
        expert_moves = self.MWU.last_expert_moves or []
        selected_expert_index = self.MWU.last_expert_sampled
        selected_expert_name = self.expert_names[int(selected_expert_index)]

        expert_losses = self.MWU.loss_computer.compute_losses(expert_moves, human_move)
        learner_loss = self.MWU.loss_computer.compute_loss(mwu_move, human_move)
        result = self._rps_result(mwu_move, human_move)

        self.MWU.update(human_move)
        weights_after = self._weights_snapshot()

        for name, loss in zip(self.expert_names, expert_losses):
            self.history["summary"]["cumulative_expert_losses"][name] += float(loss)
        self.history["summary"]["cumulative_mwu_loss"] += float(learner_loss)
        self._update_score(result)

        round_log = {
            "round": round_number,
            "human_move": self._move_payload(human_move),
            "mwu_move": self._move_payload(mwu_move),
            "selected_expert": {
                "index": int(selected_expert_index),
                "name": selected_expert_name,
            },
            "expert_moves": {
                name: self._move_payload(move)
                for name, move in zip(self.expert_names, expert_moves)
            },
            "weights_before": weights_before,
            "weights_after": weights_after,
            "losses": {
                "mwu": float(learner_loss),
                "experts": {
                    name: float(loss)
                    for name, loss in zip(self.expert_names, expert_losses)
                },
            },
            "result": result,
            "cumulative": {
                "mwu_loss": self.history["summary"]["cumulative_mwu_loss"],
                "expert_losses": dict(
                    self.history["summary"]["cumulative_expert_losses"]
                ),
                "best_expert_loss": min(
                    self.history["summary"]["cumulative_expert_losses"].values()
                ),
                "regret_to_best_expert": self.history["summary"]["cumulative_mwu_loss"]
                - min(self.history["summary"]["cumulative_expert_losses"].values()),
            },
        }

        self.history["rounds"].append(round_log)
        self.total_rounds = round_number
        self.history["summary"]["total_rounds"] = self.total_rounds

    def _finish_run(self, status):
        self._write_json_history()
        self._write_history_display()
        self._write_expert_stats_display()

        self.elements["STATUS_TEXT"].updateText(status)
        self.elements["SCORE_TEXT"].updateText(
            "Score: "
            f"MWU {self.history['summary']['mwu_wins']} | "
            f"Input {self.history['summary']['human_wins']} | "
            f"Draws {self.history['summary']['draws']}"
        )
        self.elements["ROUND_TEXT"].updateText(f"Total Rounds: {self.total_rounds}")
        if self.history_path:
            self.elements["LOG_PATH_TEXT"].updateText(
                f"Log: {os.path.relpath(self.history_path, os.getcwd())}"
            )

    def _draw_current_graph(self):
        self.MWU.draw_graph(
            show_weights=self.show_graph_weights,
            show_bound=self.show_graph_bound,
            show_expected=self.show_graph_expected,
            size=(520, 430),
            limit_timesteps=self.limit_graph_timesteps,
        )

    def _new_history(self):
        return {
            "metadata": {
                "game": "Rock-Paper-Scissors",
                "mode": "auto",
                "algorithm": "mwu_random",
                "input_file": os.path.abspath(RPS_INPUT_FILE_PATH),
                "alpha": self.alpha,
                "seed": 42,
                "experts": self.expert_names,
                "max_time_horizon": self.max_time_horizon,
                "total_input_moves": 0,
                "parse_errors": [],
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
            "rounds": [],
            "summary": {
                "total_rounds": 0,
                "mwu_wins": 0,
                "human_wins": 0,
                "draws": 0,
                "cumulative_mwu_loss": 0.0,
                "cumulative_expert_losses": {
                    name: 0.0 for name in self.expert_names
                },
            },
        }

    def _write_json_history(self):
        log_root = os.path.join(os.getcwd(), "log")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.log_dir = os.path.join(log_root, f"log_{timestamp}")
        os.makedirs(self.log_dir, exist_ok=False)
        self.history_path = os.path.join(self.log_dir, "history.json")
        self.history["metadata"]["log_dir"] = os.path.abspath(self.log_dir)

        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
            f.write("\n")

    def _write_history_display(self):
        recent_rounds = self.history["rounds"][-HISTORY_DISPLAY_LIMIT:]
        lines = ["Round | Input | MWU | Result"]

        for round_log in recent_rounds:
            lines.append(
                f"{round_log['round']:>5} | "
                f"{round_log['human_move']['name']:<8} | "
                f"{round_log['mwu_move']['name']:<8} | "
                f"{self._result_label(round_log['result'])}"
            )

        if not recent_rounds:
            lines.append("No rounds yet.")

        with open(RPS_AUTO_HISTORY_DISPLAY_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.elements["HISTORY_VIEW"].update_contents()

    def _write_expert_stats_display(self):
        cumulative_losses = self.history["summary"]["cumulative_expert_losses"]
        probabilities = self._float_list(self.MWU.probabilities)
        expert_rows = []

        for index, name in enumerate(self.expert_names):
            expert_rows.append(
                {
                    "name": name.replace("_", " "),
                    "loss": cumulative_losses[name],
                    "probability": probabilities[index],
                }
            )

        expert_rows.sort(key=lambda row: (row["loss"], -row["probability"], row["name"]))

        lines = ["Rank | Expert | Loss | Prob"]
        for rank, row in enumerate(expert_rows, start=1):
            lines.append(
                f"{rank}. {row['name']} | "
                f"L={row['loss']:.2f} | "
                f"P={row['probability']:.2f}"
            )

        with open(RPS_AUTO_EXPERT_STATS_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.elements["EXPERT_STATS_VIEW"].update_contents()

    def _weights_snapshot(self):
        return {
            "raw": self._float_list(self.MWU.raw_weights),
            "log": self._float_list(self.MWU.log_weights),
            "probabilities": self._float_list(self.MWU.probabilities),
        }

    def _update_score(self, result: str):
        if result == "mwu_win":
            self.history["summary"]["mwu_wins"] += 1
        elif result == "human_win":
            self.history["summary"]["human_wins"] += 1
        else:
            self.history["summary"]["draws"] += 1

    def _rps_result(self, mwu_move: MOVES, human_move: MOVES) -> str:
        loss = RPSLoss().compute_loss(mwu_move, human_move)
        if loss == 0.0:
            return "mwu_win"
        if loss == 0.5:
            return "draw"
        return "human_win"

    def _result_label(self, result: str):
        if result == "mwu_win":
            return "MWU wins"
        if result == "human_win":
            return "Input wins"
        return "Draw"

    def _move_payload(self, move: MOVES):
        move = MOVES(move)
        return {"name": move.name, "value": int(move)}

    def _float_list(self, values):
        return [float(value) for value in values]
