from game.util.Enums import GAMESTATE, MOVES, GAMES
from game.util import Button, get_font
from game.screens import MainMenu, GenerateInput, PlayAutoRPS, PlayAutoCF, PlayManualRPS
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
        self._generate = GenerateInput(self.screen)
        self._play_auto_rps = PlayAutoRPS(self.screen)
        self._play_auto_cf = PlayAutoCF(self.screen)
        self._play_manual_rps = PlayManualRPS(self.screen)
        
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
            
            match (self.state):
                case GAMESTATE.MENU:
                    screenReturn = self._main_menu.process(events)
                case GAMESTATE.GENERATEINPUT:
                    screenReturn = self._generate.process(events)
                case GAMESTATE.PLAYAUTORPS:
                    screenReturn = self._play_auto_rps.process(events)
                case GAMESTATE.PLAYAUTOCF:
                    screenReturn = self._play_auto_cf.process(events)
                case GAMESTATE.PLAYMANUALRPS:
                    screenReturn = self._play_manual_rps.process(events)
                case GAMESTATE.STOPPED:
                    return
            
            if screenReturn:
                if isinstance(screenReturn, GAMESTATE):
                    self.state = screenReturn
                elif isinstance(screenReturn, GAMES):
                    self._update_game(screenReturn)
                else:
                    print("ERROR: Unknown return value from current screen:", screenReturn)
                    return
            
            pygame.display.update()
            self.clock.tick(30)
    
    def _update_game(self, new_game):
        self.game = new_game
