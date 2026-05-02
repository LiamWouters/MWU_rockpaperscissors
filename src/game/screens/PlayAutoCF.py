import pygame
from game.util import GAMESTATE, GAMES, get_font, Button
from .GameScreen import *

# TODO: have a bias NumberInput that makes the coin flip "unfair"
# TODO: on the fly generate a coin toss based on the bias
# TODO: store it to the "history" (file) 

class PlayAutoCF(GameScreen):
    def __init__(self, screen):
        super().__init__(screen)
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Auto Play {GAMES.CF.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/10)),
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="BACK",
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
