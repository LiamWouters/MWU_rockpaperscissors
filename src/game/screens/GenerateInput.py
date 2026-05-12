import os
import random

import pygame

from game.util import get_font, Button, FileView, NumberInput, TextLabel, GAMESTATE, GAMES
from .GameScreen import *

RPS_INPUT_FILE_PATH = os.path.join(os.getcwd(), "RPS_input.txt")

class GenerateInput(GameScreen):
    def __init__(self, screen):
        super().__init__(screen)

        self.num_moves = 100
        self.rock_chance = 33.0
        self.paper_chance = 33.0
        self.scissors_chance = 34.0

        # Create input file if it does not exist
        open(RPS_INPUT_FILE_PATH, 'a').close()

        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Generate input for {GAMES.RPS.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/16))
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="BACK",
        )
        self.elements["COUNT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 18/100),
            font=get_font(16),
            text="Number of moves:",
        )
        self.elements["COUNT_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 22/100),
            font=get_font(16),
            fixed_width=120,
            callback=self._set_num_moves,
            start_value=self.num_moves,
            start_text="moves",
            lowerLimit=1,
        )
        self.elements["ROCK_CHANCE_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 30/100),
            font=get_font(16),
            text="Rock chance (%):",
        )
        self.elements["ROCK_CHANCE_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 34/100),
            font=get_font(16),
            fixed_width=120,
            callback=self._set_rock_chance,
            start_value=self.rock_chance,
            start_text="rock %",
            lowerLimit=0,
        )
        self.elements["PAPER_CHANCE_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 42/100),
            font=get_font(16),
            text="Paper chance (%):",
        )
        self.elements["PAPER_CHANCE_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 46/100),
            font=get_font(16),
            fixed_width=120,
            callback=self._set_paper_chance,
            start_value=self.paper_chance,
            start_text="paper %",
            lowerLimit=0,
        )
        self.elements["SCISSORS_CHANCE_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 54/100),
            font=get_font(16),
            text="Scissors chance (%):",
        )
        self.elements["SCISSORS_CHANCE_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 58/100),
            font=get_font(16),
            fixed_width=120,
            callback=self._set_scissors_chance,
            start_value=self.scissors_chance,
            start_text="scissors %",
            lowerLimit=0,
        )
        self.elements["GENERATE_BUTTON"] = Button(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 69/100),
            font=get_font(28),
            text="GENERATE",
            show_bounding_box=True,
        )
        self.elements["STATUS_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 28/100, self.screen.get_height() * 78/100),
            font=get_font(15),
            text="Ready to generate random input.",
        )
        self.elements["PREVIEW_VIEW"] = FileView(
            pos=(self.screen.get_width() * 68/100, self.screen.get_height() * 53/100),
            size=(self.screen.get_width() * 42/100, self.screen.get_height() * 70/100),
            font=get_font(14),
            file_path=RPS_INPUT_FILE_PATH,
            preamble="RPS_input.txt:",
            show_bounding_box=True,
        )

    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])

    def _handle_events(self, events):
        for event in events:
            self.elements["COUNT_INPUT"].handleEvent(event)
            self.elements["ROCK_CHANCE_INPUT"].handleEvent(event)
            self.elements["PAPER_CHANCE_INPUT"].handleEvent(event)
            self.elements["SCISSORS_CHANCE_INPUT"].handleEvent(event)
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    return GAMESTATE.MENU
                elif self.elements["COUNT_INPUT"].is_hovered():
                    self.elements["COUNT_INPUT"].toggleSelected()
                elif self.elements["ROCK_CHANCE_INPUT"].is_hovered():
                    self.elements["ROCK_CHANCE_INPUT"].toggleSelected()
                elif self.elements["PAPER_CHANCE_INPUT"].is_hovered():
                    self.elements["PAPER_CHANCE_INPUT"].toggleSelected()
                elif self.elements["SCISSORS_CHANCE_INPUT"].is_hovered():
                    self.elements["SCISSORS_CHANCE_INPUT"].toggleSelected()
                elif self.elements["GENERATE_BUTTON"].is_hovered():
                    self._generate_input()

    def _set_num_moves(self, value):
        self.num_moves = int(value)

    def _set_rock_chance(self, value):
        self.rock_chance = value

    def _set_paper_chance(self, value):
        self.paper_chance = value

    def _set_scissors_chance(self, value):
        self.scissors_chance = value

    def _generate_input(self):
        moves = ["rock", "paper", "scissors"]
        weights = [self.rock_chance, self.paper_chance, self.scissors_chance]
        total_weight = sum(weights)

        if total_weight <= 0:
            self.elements["STATUS_TEXT"].updateText("Set at least one chance above 0.")
            return

        generated_moves = random.choices(moves, weights=weights, k=self.num_moves)
        with open(RPS_INPUT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(generated_moves))
            f.write("\n")

        rock_count = generated_moves.count("rock")
        paper_count = generated_moves.count("paper")
        scissors_count = generated_moves.count("scissors")
        self.elements["STATUS_TEXT"].updateText(
            f"Generated {self.num_moves}: R {rock_count}, P {paper_count}, S {scissors_count}"
        )
        self.elements["PREVIEW_VIEW"].update_contents()
