import os, pygame
from game.util import GAMESTATE, GAMES, get_font, Button
from .GameScreen import *

# TODO: (optional) manual playing for more interactivity (presentation)

RPS_HISTORY_FILE_PATH = os.path.join(os.getcwd(), "RPS_manual_history.txt")

class PlayManualRPS(GameScreen):
    def __init__(self, screen):
        super().__init__(screen)
        
        # Create input file if it does not exist
        open(RPS_HISTORY_FILE_PATH, 'w').close()
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Manual Play {GAMES.RPS.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/16)),
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="<- BACK",
        )

    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
    
    def _handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    return GAMESTATE.MENU
