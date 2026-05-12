import copy
import json
import os
from datetime import datetime

import pygame

from algorithms import MWURegretTracker
from game import RPSLoss
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
    Panel,
    get_font,
)
from strategies import MWURandomPlayer
from strategies.RandomExpert import RandomExpert
from .GameScreen import *

RPS_HISTORY_FILE_PATH = os.path.join(os.getcwd(), "RPS_manual_history.json")
RPS_HISTORY_DISPLAY_FILE_PATH = os.path.join(os.getcwd(), "RPS_manual_history.txt")
RPS_EXPERT_STATS_FILE_PATH = os.path.join(os.getcwd(), "RPS_manual_expert_stats.txt")
HISTORY_DISPLAY_LIMIT = 10


class PlayManualRPS(GameScreen):
    def __init__(self, screen, experts=None):
        super().__init__(screen)

        self.experts = experts or {"random": RandomExpert(MOVES)}
        self.expert_names = [str(name) for name in self.experts.keys()]
        self.alpha = 0.5
        self.max_time_horizon = 200
        self.show_graph_weights = True
        self.show_graph_winrate = False
        self.show_graph_ratio = False
        self.show_graph_bound = True
        self.show_graph_expected = True
        self.limit_graph_timesteps = 0

        # Create history files if they do not exist.
        open(RPS_HISTORY_FILE_PATH, "w", encoding="utf-8").close()
        open(RPS_HISTORY_DISPLAY_FILE_PATH, "w", encoding="utf-8").close()
        open(RPS_EXPERT_STATS_FILE_PATH, "w", encoding="utf-8").close()

        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(
            f"Manual Play {GAMES.RPS.value}", True, white
        )
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(
            center=(self.screen.get_width() / 2, self.screen.get_height() / 16)
        )
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="<- BACK",
        )
        
        # Algorithm settings
        self.elements["ALPHA_INPUT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 47 / 100, self.screen.get_height() * 87 / 100),
            font=get_font(16),
            text="Set Alpha (LR):",
        )
        self.elements["ALPHA_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 47 / 100, self.screen.get_height() * 90 / 100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_alpha,
            start_value=self.alpha,
            start_text="alpha",
            lowerLimit=0,
            upperLimit=0.5,
        )
        self.elements["MAX_T_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 47 / 100, self.screen.get_height() * 93 / 100),
            font=get_font(16),
            text="Set max time horizon:",
        )
        self.elements["MAX_T_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 47 / 100, self.screen.get_height() * 96 / 100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_max_time_horizon,
            start_value=self.max_time_horizon,
            start_text="time horizon",
            lowerLimit=1,
        )
        self.elements["ALGORITHM_SETTINGS_PANEL"] = Panel(
            elements=[
                self.elements["ALPHA_INPUT_TEXT"],
                self.elements["ALPHA_INPUT"],
                self.elements["MAX_T_TEXT"],
                self.elements["MAX_T_INPUT"]
            ],
            x_padding=6,
            y_padding=4
        )
        
        self.elements["ROCK_BUTTON"] = Button(
            pos=(self.screen.get_width() * 47 / 100, self.screen.get_height() * 81 / 100),
            font=get_font(28),
            text="ROCK",
            show_bounding_box=True,
        )
        self.elements["PAPER_BUTTON"] = Button(
            pos=(self.screen.get_width() * 65 / 100, self.screen.get_height() * 81 / 100),
            font=get_font(28),
            text="PAPER",
            show_bounding_box=True,
        )
        self.elements["SCISSORS_BUTTON"] = Button(
            pos=(self.screen.get_width() * 85 / 100, self.screen.get_height() * 81 / 100),
            font=get_font(28),
            text="SCISSORS",
            show_bounding_box=True,
        )
        
        self.elements["HUMAN_MOVE"] = TextLabel(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 16 / 100),
            font=get_font(18),
            text="Your Move:",
        )
        self.elements["MWU_MOVE"] = TextLabel(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 20 / 100),
            font=get_font(18),
            text="MWU Move:",
        )
        self.elements["ROUND_RESULT"] = TextLabel(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 25 / 100),
            font=get_font(18),
            text="Result:",
        )
        self.elements["SCORE_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 31 / 100),
            font=get_font(16),
            text="Score: MWU 0 | You 0 | Draws 0",
        )
        self.elements["ROUND_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 35 / 100),
            font=get_font(16),
            text="Total Rounds: 0",
        )
        self.elements["DATA_PANEL"] = Panel(
            elements=[
                self.elements["HUMAN_MOVE"],
                self.elements["MWU_MOVE"],
                self.elements["ROUND_RESULT"],
                self.elements["SCORE_TEXT"],
                self.elements["ROUND_TEXT"],
            ]
        )
        
        # Expert ranking file
        self.elements["EXPERT_STATS_VIEW"] = FileView(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 89 / 100),
            size=(self.screen.get_width() * 32 / 100, self.screen.get_height() * 17 / 100),
            font=get_font(12),
            file_path=RPS_EXPERT_STATS_FILE_PATH,
            preamble="EXPERT RANKING:",
            show_bounding_box=True,
        )
        # History (last 10 rounds)
        self.elements["HISTORY_VIEW"] = FileView(
            pos=(self.screen.get_width() * 18 / 100, self.screen.get_height() * 60 / 100),
            size=(self.screen.get_width() * 32 / 100, self.screen.get_height() * 35 / 100),
            font=get_font(12),
            file_path=RPS_HISTORY_DISPLAY_FILE_PATH,
            preamble="LAST 10 AUTO ROUNDS:",
            show_bounding_box=True,
        )
        self.elements["FILE_VIEWS_PANEL"] = Panel(
            elements=[self.elements["HISTORY_VIEW"], self.elements["EXPERT_STATS_VIEW"]],
            x_padding=4,
            y_padding=4
        )

        ### GRAPH
        self.elements["GRAPH_VIEW"] = ImageView(
            pos=(self.screen.get_width() * 67 / 100, self.screen.get_height() * 44 / 100),
            image=None,
            show_bounding_box=False,
        )
        self.elements["GRAPH_VIEW_PANEL"] = Panel(
            elements=[self.elements["GRAPH_VIEW"]],
            x_padding=2,
            y_padding=2
        )
        
        ## Graph settings
        self.elements["GRAPH_LIMIT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 70/100, self.screen.get_height() * 87/100),
            font=get_font(16),
            text="Set timestep limit:"
        )
        self.elements["GRAPH_LIMIT_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 70/100, self.screen.get_height() * 90/100),
            font=get_font(16),
            fixed_width=100,
            callback=self._set_timestep_limit,
            start_value=self.limit_graph_timesteps,
            start_text="timestep limit",
            lowerLimit=-1
        )
        self.elements["GRAPH_EXPECTED_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 70/100, self.screen.get_height() * 93/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide expected loss"
        )
        self.elements["GRAPH_BOUND_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 70/100, self.screen.get_height() * 96/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide bound"
        )
        self.elements["GRAPH_WEIGHTS_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 90/100, self.screen.get_height() * 87/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide weights"
        )
        self.elements["GRAPH_WINRATE_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 90/100, self.screen.get_height() * 90/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide winrate"
        )
        self.elements["GRAPH_RATIO_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 90/100, self.screen.get_height() * 93/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide ratios"
        )
        self.elements["GRAPH_SETTINGS_PANEL"] = Panel(
            elements=[
                self.elements["GRAPH_LIMIT_TEXT"],
                self.elements["GRAPH_LIMIT_INPUT"],
                self.elements["GRAPH_EXPECTED_TOGGLE"],
                self.elements["GRAPH_BOUND_TOGGLE"],
                self.elements["GRAPH_WINRATE_TOGGLE"],
                self.elements["GRAPH_WEIGHTS_TOGGLE"],
                self.elements["GRAPH_RATIO_TOGGLE"],
            ],
            x_padding=2,
            y_padding=2
        )

        self.reset()

    def _draw(self):
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
                elif self.elements["ROCK_BUTTON"].is_hovered():
                    self._play_round(MOVES.ROCK)
                elif self.elements["PAPER_BUTTON"].is_hovered():
                    self._play_round(MOVES.PAPER)
                elif self.elements["SCISSORS_BUTTON"].is_hovered():
                    self._play_round(MOVES.SCISSORS)
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
                elif self.elements["GRAPH_RATIO_TOGGLE"].is_hovered():
                    self.elements["GRAPH_RATIO_TOGGLE"].switch()
                    self.show_graph_ratio = not self.elements["GRAPH_RATIO_TOGGLE"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_WINRATE_TOGGLE"].is_hovered():
                    self.elements["GRAPH_WINRATE_TOGGLE"].switch()
                    self.show_graph_winrate = not self.elements["GRAPH_WINRATE_TOGGLE"].state
                    self._draw_current_graph()

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

    def _draw_current_graph(self, save_to_file: bool = False):
        self.MWU.draw_graph(
            show_weights=self.show_graph_weights,
            show_bound=self.show_graph_bound,
            show_expected=self.show_graph_expected,
            show_ratio=self.show_graph_ratio,
            show_winrate=self.show_graph_winrate,
            size=(750, 465),
            limit_timesteps=self.limit_graph_timesteps,
            save_to_file=save_to_file
        )

    def _play_round(self, human_move: MOVES):
        if self.total_rounds >= self.MWU.regret_tracker._max_t:
            self.elements["ROUND_RESULT"].updateText("Result: max time horizon reached")
            self._draw_current_graph(save_to_file=True)
            return

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
        self._write_history()
        self._write_history_display()
        self._write_expert_stats_display()

        self.elements["HUMAN_MOVE"].updateText(f"Your Move: {human_move.name}")
        self.elements["MWU_MOVE"].updateText(f"MWU Move: {mwu_move.name}")
        self.elements["ROUND_RESULT"].updateText(
            f"Result: {self._result_label(result)}"
        )
        self.elements["SCORE_TEXT"].updateText(
            "Score: "
            f"MWU {self.history['summary']['mwu_wins']} | "
            f"You {self.history['summary']['human_wins']} | "
            f"Draws {self.history['summary']['draws']}"
        )
        self.elements["ROUND_TEXT"].updateText(f"Total Rounds: {self.total_rounds}")
        self._draw_current_graph()

    def reset(self):
        self.total_rounds = 0
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
        self.history = {
            "metadata": {
                "game": "Rock-Paper-Scissors",
                "mode": "manual",
                "algorithm": "mwu_random",
                "history_file": os.path.abspath(RPS_HISTORY_FILE_PATH),
                "alpha": self.alpha,
                "seed": 42,
                "experts": self.expert_names,
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
        self._write_history()
        self._write_history_display()
        self._write_expert_stats_display()

        self.elements["HUMAN_MOVE"].updateText("Your Move:")
        self.elements["MWU_MOVE"].updateText("MWU Move:")
        self.elements["ROUND_RESULT"].updateText("Result:")
        self.elements["SCORE_TEXT"].updateText("Score: MWU 0 | You 0 | Draws 0")
        self.elements["ROUND_TEXT"].updateText("Total Rounds: 0")
        self.elements["GRAPH_VIEW"].clear()
        
        # Start toggles switched on if they should be (and arent)
        if not self.show_graph_ratio and not self.elements["GRAPH_RATIO_TOGGLE"].state:   
            self.elements["GRAPH_RATIO_TOGGLE"].switch()
        if not self.show_graph_winrate and not self.elements["GRAPH_WINRATE_TOGGLE"].state:
            self.elements["GRAPH_WINRATE_TOGGLE"].switch()
        if not self.show_graph_weights and not self.elements["GRAPH_WEIGHTS_TOGGLE"].state:
            self.elements["GRAPH_WEIGHTS_TOGGLE"].switch()
        if not self.show_graph_expected and not self.elements["GRAPH_EXPECTED_TOGGLE"].state:
            self.elements["GRAPH_EXPECTED_TOGGLE"].switch()
        if not self.show_graph_bound and not self.elements["GRAPH_BOUND_TOGGLE"].state:
            self.elements["GRAPH_BOUND_TOGGLE"].switch()
            
        self._draw_current_graph()

    def _write_history(self):
        with open(RPS_HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
            f.write("\n")

    def _write_history_display(self):
        recent_rounds = self.history["rounds"][-HISTORY_DISPLAY_LIMIT:]
        lines = ["Round | You | MWU | Result"]

        for round_log in recent_rounds:
            lines.append(
                f"{round_log['round']:>5} | "
                f"{round_log['human_move']['name']:<8} | "
                f"{round_log['mwu_move']['name']:<8} | "
                f"{self._result_label(round_log['result'])}"
            )

        if not recent_rounds:
            lines.append("No rounds yet.")

        with open(RPS_HISTORY_DISPLAY_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.elements["HISTORY_VIEW"].update_contents()

    def _write_expert_stats_display(self):
        cumulative_losses = self.history["summary"]["cumulative_expert_losses"]
        probabilities = self._float_list(self.MWU.probabilities)
        raw_weights = self._float_list(self.MWU.raw_weights)
        expert_rows = []

        for index, name in enumerate(self.expert_names):
            expert_rows.append(
                {
                    "name": name.replace("_", " "),
                    "loss": cumulative_losses[name],
                    "probability": probabilities[index],
                    "weight": raw_weights[index],
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

        with open(RPS_EXPERT_STATS_FILE_PATH, "w", encoding="utf-8") as f:
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

    def _result_label(self, result: str) -> str:
        if result == "mwu_win":
            return "MWU wins"
        if result == "human_win":
            return "You win"
        return "Draw"

    def _move_payload(self, move: MOVES):
        move = MOVES(move)
        return {"name": move.name, "value": int(move)}

    def _float_list(self, values):
        return [float(value) for value in values]
