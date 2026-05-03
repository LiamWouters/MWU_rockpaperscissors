import os, pygame
from game.util import GAMESTATE, MOVES, GAMES, get_font, Button
from .GameScreen import *

RPS_INPUT_FILE_PATH = os.path.join(os.getcwd(), "RPS_input.txt")

class PlayAutoRPS(GameScreen):
    def __init__(self, screen):
        super().__init__(screen)
        
        # Create input file if it does not exist
        open(RPS_INPUT_FILE_PATH, 'a').close()
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Auto Play {GAMES.RPS.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/16)),
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

