import pygame, os, random, time
from game import CFLoss
from game.util import GAMESTATE, GAMES, COINFACE, get_font, Button, FileView, NumberInput, TextLabel, Switch
from algorithms import WeightedMajorityRegretTracker, MWURegretTracker
from strategies import WeightedMajorityPlayer, MWURandomPlayer
from .GameScreen import *

CF_HISTORY_FILE_PATH = os.path.join(os.getcwd(), "CF_history.txt")
CF_SUMMARY_FILE_PATH = os.path.join(os.getcwd(), "CF_history_summary.txt")

def get_time_milliseconds():
    return int(time.time() * 1000)

class PlayCF(GameScreen):
    def __init__(self, screen, experts: dict):
        super().__init__(screen)
        
        # Persistent (cant reset)
        self.experts = experts
        self.heads_chance = 50.0
        self.alpha = 0.5
        self.interval = 100 # in milliseconds
        
        # Initialize persistent elements
        self.elements["TITLE_TEXT"] = get_font(34).render(f"Auto Play {GAMES.CF.value}", True, white)
        self.elements["TITLE_RECT"] = self.elements["TITLE_TEXT"].get_rect(center=(self.screen.get_width()/2,self.screen.get_height()/16)),
        self.elements["BACK_BUTTON"] = Button(
            pos=(100, 50),
            font=get_font(18),
            text="BACK",
        )
        self.elements["HISTORY_VIEW"] = FileView(
            pos=(self.screen.get_width() * 10/100, self.screen.get_height() * 50/100),
            size=(self.screen.get_width() * 10/100, self.screen.get_height() * 75/100),
            font=get_font(14),
            file_path=CF_HISTORY_FILE_PATH,
            preamble="HISTORY:",
            show_bounding_box=True
        )
        self.elements["HEADS_CHANCE_INPUT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 15/100),
            font=get_font(16),
            text="Set Heads Chance (%):"
        )
        self.elements["HEADS_CHANCE_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 18/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_heads_chance,
            start_value=self.heads_chance,
            start_text="heads chance",
            lowerLimit=0,
            upperLimit=100
        )
        self.elements["ALPHA_INPUT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 22/100),
            font=get_font(16),
            text="Set Alpha (LR):"
        )
        self.elements["ALPHA_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 25/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_alpha,
            start_value=self.alpha,
            start_text="alpha",
            lowerLimit=0,
            upperLimit=1
        )
        self.elements["AUTO_INTERVAL_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 29/100),
            font=get_font(16),
            text="Set auto interval (ms):"
        )
        self.elements["AUTO_INTERVAL_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 32/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_interval,
            start_value=self.interval,
            start_text="interval",
            lowerLimit=0
        )
        self.elements["AUTO_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 36/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Auto Play",
            show_bounding_box=True
        )
        self.elements["ROLL_BUTTON"] = Button(
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 50/100),
            font=get_font(35),
            text="FLIP COIN",
            show_bounding_box=True
        )
        self.elements["LATEST_ROLL"] = TextLabel(
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 55/100),
            font=get_font(18),
            text="Latest Roll:",
        )
        self.elements["TOTAL_ROLLS"] = TextLabel(
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 59/100),
            font=get_font(16),
            text=f"Total Rolls:",
        )
        
        self.reset()

    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
    
    def _handle_events(self, events):
        if self.auto_move and (get_time_milliseconds() - self.last_move_time > self.interval):
            self._roll_coin()
            
        for event in events:
            self.elements["HEADS_CHANCE_INPUT"].handleEvent(event)
            self.elements["ALPHA_INPUT"].handleEvent(event)
            self.elements["AUTO_INTERVAL_INPUT"].handleEvent(event)
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    self.reset()
                    return GAMESTATE.MENU
                elif self.elements["HEADS_CHANCE_INPUT"].is_hovered():
                    self.elements["HEADS_CHANCE_INPUT"].toggleSelected()
                elif self.elements["ALPHA_INPUT"].is_hovered():
                    self.elements["ALPHA_INPUT"].toggleSelected()
                elif self.elements["AUTO_INTERVAL_INPUT"].is_hovered():
                    self.elements["AUTO_INTERVAL_INPUT"].toggleSelected()
                elif self.elements["AUTO_TOGGLE"].is_hovered():
                    self.elements["AUTO_TOGGLE"].switch()
                    self.auto_move = self.elements["AUTO_TOGGLE"].state
                elif self.elements["ROLL_BUTTON"].is_hovered():
                    self._roll_coin()
                
    def _set_heads_chance(self, value):
        self.heads_chance = value
    
    def _set_alpha(self, value):
        if (self.alpha == value):
            return
        self.alpha = value
        self.reset()    # Reset to load learners with new alpha
    
    def _set_interval(self, value):
        self.interval = value
        
    def _roll_coin(self):
        normalized_heads_chance = self.heads_chance/100
        self.latest_roll = random.choices([face for face in COINFACE], weights=(1-normalized_heads_chance, normalized_heads_chance))[0]
        latest_roll_text = "HEADS" if self.latest_roll == COINFACE.HEADS else "TAILS"
        self.total_rolls += 1
        self.last_move_time = get_time_milliseconds()
        
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll: {self.latest_roll}")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        
        ## Update learners
        mwu_guess = self.MWU.play([])   # TODO: give game history?
        self.MWU.update(self.latest_roll)
        print(f"mwu_guess: {mwu_guess}, was: {self.latest_roll} ({latest_roll_text})")
        
        ## SAVE TO FILE
        # Store to history file
        with open(CF_HISTORY_FILE_PATH, 'a') as f: 
            f.write(f"{latest_roll_text},\n")
        
        # Change file being viewed 
        if self.total_rolls > 10:
            self._create_summary_file()
            self.elements["HISTORY_VIEW"].change_file(CF_SUMMARY_FILE_PATH)
        else:
            self.elements["HISTORY_VIEW"].change_file(CF_HISTORY_FILE_PATH)
            
    def _create_summary_file(self):
        heads_count = 0
        tails_count = 0
        lastMoves = []
        limit = 10
        with open(CF_HISTORY_FILE_PATH, 'r') as f:
            for line in f:
                move = line.strip().replace(',','')
                if move == "HEADS":
                    heads_count += 1
                elif move == "TAILS":
                    tails_count += 1
                else:
                    print(f"ERROR: corrupt coin flip history file ({move})")
                lastMoves.insert(0, move)
                lastMoves = lastMoves[:limit]
        
        with open(CF_SUMMARY_FILE_PATH, 'w') as f:
            f.write(f"HEADS (x{heads_count})\nTAILS (x{tails_count})\n \nlast {limit} moves:\n{'\n'.join(lastMoves)}") 
    
    def reset(self):
        # Reset values
        open(CF_HISTORY_FILE_PATH, 'w').close()
        open(CF_SUMMARY_FILE_PATH, 'w').close()
        self.latest_roll = None
        self.total_rolls = 0
        self.auto_move = False
        self.last_move_time = get_time_milliseconds()
        
        # Reset learners (MWU, WM)
        self.MWU = MWURandomPlayer(
            experts=self.experts.values(),
            loss_computer=CFLoss(),
            moves_enum=COINFACE,
            alpha=self.alpha,
            regret_tracker=MWURegretTracker(len(self.experts), self.alpha, max_t=200),
            seed=42
        )
        self.WM = None
        
        # Reset UI
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll:")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        self.elements["HISTORY_VIEW"].update_contents()
