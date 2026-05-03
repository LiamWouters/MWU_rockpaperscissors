import pygame
from .GameScreen import *
from game.util import get_font, UIelement, Button, Switch, NumberInput, GAMESTATE, GAMES

class MainMenu(GameScreen):
    def __init__(self, screen, game: GAMES):
        super().__init__(screen)
        self.selected_game = game
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"MWU {self.selected_game.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6)),
        self.elements["PLAY_AUTO_BUTTON"] = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
            font=get_font(18),
            text="Play Auto",
            show_bounding_box=False
        )
        self.elements["GENERATE_INPUT_BUTTON"] = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 3/6),
            font=get_font(18),
            text="Generate Input (For Play Auto)",
            show_bounding_box=False
        )
        self.elements["PLAY_MANUAL_BUTTON"] = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 4/6),
            font=get_font(18),
            text="Play Manual",
            show_bounding_box=False
        )
        self.elements["QUIT_BUTTON"] = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 5/6),
            font=get_font(18),
            text="Quit",
            show_bounding_box=False
        )
        self.elements["GAME_SWITCH"] = Switch(
            pos=(250, 50),
            slider_size=(50,20),
            option1text="Rock Paper Scissors",
            option2text="Coin Flip",
            font = get_font(14),
            show_bounding_box=False
        )
        
    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
    
    def _handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["PLAY_MANUAL_BUTTON"].is_hovered():
                    if self.selected_game == GAMES.RPS:
                        return GAMESTATE.PLAYMANUALRPS
                    else:
                        return GAMESTATE.PLAYMANUALCF
                elif self.elements["PLAY_AUTO_BUTTON"].is_hovered():
                    if self.selected_game == GAMES.RPS:
                        return GAMESTATE.PLAYAUTORPS
                    else:
                        return GAMESTATE.PLAYAUTOCF
                elif self.elements["GENERATE_INPUT_BUTTON"].is_hovered():
                    return GAMESTATE.GENERATEINPUT
                elif self.elements["QUIT_BUTTON"].is_hovered():
                    return GAMESTATE.STOPPED
                elif self.elements["GAME_SWITCH"].is_hovered():
                    self.elements["GAME_SWITCH"].switch()
                    self.toggleMenu(self.elements["GAME_SWITCH"].state)
                    return self.selected_game
    
    def toggleMenu(self, is_cf: bool):
        self.selected_game = GAMES.CF if is_cf else GAMES.RPS
        self.updateTitle(f"MWU {self.selected_game.value}")
        
        # Change elements
        self.elements["PLAY_MANUAL_BUTTON"].active = not is_cf
        self.elements["GENERATE_INPUT_BUTTON"].active = not is_cf
    
    def updateTitle(self, newTitle):
        self.elements["TITLE_TEXT"] = get_font(34).render(newTitle, True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6)),
