from enum import Enum
from game import MOVES
from game.util import Button
import pygame

class GAMESTATE(Enum):
    STOPPED = 0,
    MENU = 1,
    MANUAL = 2,
    AUTO = 3,
    
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

# TODO: load persistent objects such as buttons once during __init__ instead of every frame

class RPS:
    def __init__(self, experts: dict, screenwidth=750, screenheight=750):
        self.experts = experts
        
        # Start pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((screenwidth, screenheight))
        self.clock = pygame.time.Clock()
        self.state = GAMESTATE.MENU
        
        # Start game loop
        self._game_loop()
        
        pygame.quit()
        
    def _get_font(self, size) -> pygame.font.Font:
        return pygame.font.SysFont("monocraft", size)
    
    def _game_loop(self):
        # State machine
        while self.state != GAMESTATE.STOPPED:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.state = GAMESTATE.STOPPED
            
            if self.state == GAMESTATE.MENU:
                self._menu(events)
            if self.state == GAMESTATE.MANUAL:
                self._play_manual(events)
            if self.state == GAMESTATE.AUTO:
                self._play_auto(events)
            
            pygame.display.update()
            self.clock.tick(30)
    
    def _menu(self, events):
        pygame.display.set_caption("MWU | Rock Paper Scissors | Main Menu")
        
        PLAY_MANUAL_BUTTON = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
            width=100,
            height=50,
            font=self._get_font(18),
            text="Play Manual"
        )
        
        PLAY_AUTO_BUTTON = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 3/6),
            width=100,
            height=50,
            font=self._get_font(18),
            text="Play Auto"
        )
        
        QUIT_BUTTON = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 4/6),
            width=100,
            height=50,
            font=self._get_font(18),
            text="Quit",
        )
            
        # Create menu screen
        self.screen.fill("black")
        TITLE_TEXT = self._get_font(34).render("MWU Rock-Paper-Scissors", True, white)
        TITLE_RECT = TITLE_TEXT.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6))
        
        self.screen.blit(TITLE_TEXT, TITLE_RECT)
        
        # Draw all buttons
        for button in [PLAY_MANUAL_BUTTON, PLAY_AUTO_BUTTON, QUIT_BUTTON]:
            button.draw(self.screen)    
        
        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                self.state = GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if PLAY_MANUAL_BUTTON.is_hovered():
                    self.state = GAMESTATE.MANUAL
                    return
                elif PLAY_AUTO_BUTTON.is_hovered():
                    self.state = GAMESTATE.AUTO
                    return
                elif QUIT_BUTTON.is_hovered():
                    self.state = GAMESTATE.STOPPED
                    return
        
    def _play_manual(self, events):
        pygame.display.set_caption("MWU | Rock Paper Scissors | Manual Play")
        
        # Persistent objects
        BACK_BUTTON = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
            width=100,
            height=50,
            font=self._get_font(18),
            text="BACK",
        )
        
        self.screen.fill("black")
        
        # Placeholder
        PLACEHOLDER_TEXT = self._get_font(34).render("MANUAL PLAY (PLACEHOLDER)", True, white)
        PLACEHOLDER_RECT = PLACEHOLDER_TEXT.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6))
        self.screen.blit(PLACEHOLDER_TEXT, PLACEHOLDER_RECT)
        
        for button in [BACK_BUTTON]:
            button.draw(self.screen)
            
        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                self.state = GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if BACK_BUTTON.is_hovered():
                    self.state = GAMESTATE.MENU
                    return    
    
    def _play_auto(self, events):
        pygame.display.set_caption("MWU | Rock Paper Scissors | Auto Play")
        
        # Persistent Objects
        BACK_BUTTON = Button(
            pos=(self.screen.get_width()/2, self.screen.get_height()* 2/6),
            width=100,
            height=50,
            font=self._get_font(18),
            text="BACK",
        )
        
        self.screen.fill("black")
        
        # Placeholder
        PLACEHOLDER_TEXT = self._get_font(34).render("AUTO PLAY (PLACEHOLDER)", True, white)
        PLACEHOLDER_RECT = PLACEHOLDER_TEXT.get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/6))
        self.screen.blit(PLACEHOLDER_TEXT, PLACEHOLDER_RECT)
        
        for button in [BACK_BUTTON]:
            button.draw(self.screen)
            
        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                self.state = GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if BACK_BUTTON.is_hovered():
                    self.state = GAMESTATE.MENU
                    return
            
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
