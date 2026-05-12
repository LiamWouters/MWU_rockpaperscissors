import os, pygame
from game.auto_play import run_rps_auto_play
from game.util import GAMESTATE, MOVES, GAMES, get_font, Button, FileView, TextLabel
from .GameScreen import *
from strategies.RandomExpert import RandomExpert

RPS_INPUT_FILE_PATH = os.path.join(os.getcwd(), "RPS_input.txt")

class PlayAutoRPS(GameScreen):
    def __init__(self, screen, experts=None):
        super().__init__(screen)
        self.experts = experts or {"random": RandomExpert(MOVES)}
        self._has_run = False
        self._last_result = None
        
        # Create input file if it does not exist
        open(RPS_INPUT_FILE_PATH, 'a').close()
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Auto Play {GAMES.RPS.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/16)),
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="<- BACK",
        )
        self.elements["STATUS_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 50/100, self.screen.get_height() * 16/100),
            font=get_font(18),
            text="Preparing auto run...",
        )
        self.elements["LOG_PATH_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 50/100, self.screen.get_height() * 21/100),
            font=get_font(14),
            text=""
        )

    def _draw(self):
        self._ensure_auto_play_ran()
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
    
    def _handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    self.reset()
                    return GAMESTATE.MENU

    def _ensure_auto_play_ran(self):
        if self._has_run:
            return

        self._has_run = True
        self._last_result = run_rps_auto_play(
            input_file_path=RPS_INPUT_FILE_PATH,
            experts=self.experts,
        )

        history = self._last_result["history"]
        total_rounds = history["summary"]["total_rounds"]
        parse_error_count = len(history["metadata"]["parse_errors"])
        status = f"Auto run complete: {total_rounds} rounds"
        if parse_error_count:
            status += f" ({parse_error_count} invalid input tokens skipped)"

        self.elements["STATUS_TEXT"].updateText(status)
        history_path_display = os.path.relpath(
            self._last_result["history_path"],
            os.getcwd(),
        )
        self.elements["LOG_PATH_TEXT"].updateText(f"Log: {history_path_display}")
        self.elements["HISTORY_VIEW"] = FileView(
            pos=(self.screen.get_width() * 50/100, self.screen.get_height() * 57/100),
            size=(self.screen.get_width() * 75/100, self.screen.get_height() * 60/100),
            font=get_font(13),
            file_path=self._last_result["history_path"],
            preamble="history.json:",
            show_bounding_box=True
        )

    def reset(self):
        self._has_run = False

    # HELPERS
    def _determine_winner(self, move1: MOVES, move2: MOVES):
        """
            Rock (0) beats Scissors (1),
            Scissors (1) beats Paper (2),
            Paper (2) beats Rock (0),
            
            Returns:
             - None in case of a draw
             - 1 if move1 wins
             - 2 if move2 wins
        """
        dif = (move1 - move2)%3
        print(f"{move1.name} vs. {move2.name}:")
        if dif == 0: 
            print(f"  -> {None}")
            return None # Draw
        elif dif == 1:
            print(f"  -> {move2.name}") 
            return 2
        elif dif == 2: 
            print(f"  -> {move1.name}")
            return 1 

