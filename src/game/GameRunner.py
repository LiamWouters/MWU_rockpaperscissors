from game.util.Enums import GAMESTATE, MOVES, GAMES
from game.util import Button, get_font
from game.screens import MainMenu
import pygame

class GameRunner:
    def __init__(self, experts: dict, screenwidth=1280, screenheight=720):
        self.experts = experts
        
        # Start pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((screenwidth, screenheight))
        self.clock = pygame.time.Clock()
        self.state = GAMESTATE.MENU
        
        self.game = GAMES.RPS
        
        # Initialize screens
        self._main_menu = MainMenu(self.screen, self.game)
        
        # Start game loop
        self._game_loop()
        
        pygame.quit()
    
    def _game_loop(self):
        # State machine
        while self.state != GAMESTATE.STOPPED:
            events = pygame.event.get()
            screenReturn = None
            for event in events:
                if event.type == pygame.QUIT:
                    self.state = GAMESTATE.STOPPED
            
            if self.state == GAMESTATE.MENU:
                screenReturn = self._main_menu.process(events)
            elif self.state == GAMESTATE.MANUAL:
                # self._play_manual(events)
                pass
            elif self.state == GAMESTATE.AUTO:
                # self._play_auto(events)
                pass
            
            if screenReturn:
                if isinstance(screenReturn, GAMESTATE):
                    self.state = screenReturn
                elif isinstance(screenReturn, GAMES):
                    self.game = screenReturn
                    print(self.game)
                else:
                    print("ERROR: Unknown return value from current screen:", screenReturn)
                    return
            
            pygame.display.update()
            self.clock.tick(30)
    
    ####### PLACEHOLDERS #######
    # def _play_manual(self, events):
    #     pygame.display.set_caption("MWU | Rock Paper Scissors | Manual Play")
        
    #     # Persistent objects
    #     BACK_BUTTON = Button(
    #         pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
    #         width=100,
    #         height=50,
    #         font=get_font(18),
    #         text="BACK",
    #     )
        
    #     self.screen.fill("black")
        
    #     # Placeholder
    #     PLACEHOLDER_TEXT = get_font(34).render("MANUAL PLAY (PLACEHOLDER)", True, white)
    #     PLACEHOLDER_RECT = PLACEHOLDER_TEXT.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6))
    #     self.screen.blit(PLACEHOLDER_TEXT, PLACEHOLDER_RECT)
        
    #     for button in [BACK_BUTTON]:
    #         button.draw(self.screen)
            
    #     # Handle events
    #     for event in events:
    #         if event.type == pygame.QUIT:
    #             self.state = GAMESTATE.STOPPED
    #         if event.type == pygame.MOUSEBUTTONUP:
    #             if BACK_BUTTON.is_hovered():
    #                 self.state = GAMESTATE.MENU
    #                 return    
    
    # def _play_auto(self, events):
    #     pygame.display.set_caption("MWU | Rock Paper Scissors | Auto Play")
        
    #     # Persistent Objects
    #     BACK_BUTTON = Button(
    #         pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
    #         width=100,
    #         height=50,
    #         font=get_font(18),
    #         text="BACK",
    #     )
        
    #     self.screen.fill("black")
        
    #     # Placeholder
    #     PLACEHOLDER_TEXT = get_font(34).render("AUTO PLAY (PLACEHOLDER)", True, white)
    #     PLACEHOLDER_RECT = PLACEHOLDER_TEXT.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6))
    #     self.screen.blit(PLACEHOLDER_TEXT, PLACEHOLDER_RECT)
        
    #     for button in [BACK_BUTTON]:
    #         button.draw(self.screen)
            
    #     # Handle events
    #     for event in events:
    #         if event.type == pygame.QUIT:
    #             self.state = GAMESTATE.STOPPED
    #         if event.type == pygame.MOUSEBUTTONUP:
    #             if BACK_BUTTON.is_hovered():
    #                 self.state = GAMESTATE.MENU
    #                 return
                
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
