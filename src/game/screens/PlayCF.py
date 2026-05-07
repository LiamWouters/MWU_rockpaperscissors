import pygame, os, random, time
from game import CFLoss
from game.util import GAMESTATE, GAMES, COINFACE, get_font, Button, FileView, NumberInput, TextLabel, Switch, ImageView
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
        self.max_time_horizon = 200
        
        self.show_graph_weights = True
        self.show_graph_bound = True
        self.show_graph_expected = True
        self.limit_graph_timesteps = 0  # 0 or lower means no limit
        self.current_mwu = True # False means to show WM graph instead of MWU's
        
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
        self.elements["MAX_T_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 29/100),
            font=get_font(16),
            text="Set max time horizon:"
        )
        self.elements["MAX_T_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 32/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_max_time_horizon,
            start_value=self.max_time_horizon,
            start_text="time horizon",
            lowerLimit=1
        )
        self.elements["AUTO_INTERVAL_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 36/100),
            font=get_font(16),
            text="Set auto interval (ms):"
        )
        self.elements["AUTO_INTERVAL_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 39/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_interval,
            start_value=self.interval,
            start_text="interval",
            lowerLimit=0
        )
        self.elements["AUTO_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 43/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Auto Play"
        )
        self.elements["ROLL_BUTTON"] = Button(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 50/100),
            font=get_font(35),
            text="FLIP COIN",
            show_bounding_box=True
        )
        self.elements["LATEST_ROLL"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 55/100),
            font=get_font(18),
            text="Latest Roll:",
        )
        self.elements["TOTAL_ROLLS"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 59/100),
            font=get_font(16),
            text=f"Total Rolls:",
        )
        self.elements["PREDICTION_MWU"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 66/100),
            font=get_font(18),
            text="MWU Prediction:",
        )
        self.elements["PREDICTION_WM"] = TextLabel(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 70/100),
            font=get_font(18),
            text="WM Prediction:",
        )
        self.elements["GRAPH_SWITCH"] = Switch(
            pos=(self.screen.get_width() * 27/100, self.screen.get_height() * 80/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="MWU",
            option2text="WM"
        )
        
        ### GRAPH
        self.elements["GRAPH_VIEW"] = ImageView(
            pos=(self.screen.get_width() * 70/100, self.screen.get_height() * 50/100),
            image=None,
            show_bounding_box=False,
        ) 
        # Graph settings
        self.elements["GRAPH_LIMIT_TEXT"] = TextLabel(
            pos=(self.screen.get_width() * 60/100, self.screen.get_height() * 87/100),
            font=get_font(16),
            text="Set timestep limit:"
        )
        self.elements["GRAPH_LIMIT_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 60/100, self.screen.get_height() * 90/100),
            font=get_font(16),
            fixed_width=100,
            callback=self._set_timestep_limit,
            start_value=self.limit_graph_timesteps,
            start_text="timestep limit",
            lowerLimit=-1
        )
        self.elements["GRAPH_EXPECTED_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 80/100, self.screen.get_height() * 87/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide expected loss"
        )
        self.elements["GRAPH_BOUND_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 80/100, self.screen.get_height() * 90/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide bound"
        )
        self.elements["GRAPH_WEIGHTS_TOGGLE"] = Switch(
            pos=(self.screen.get_width() * 80/100, self.screen.get_height() * 93/100),
            font=get_font(16),
            slider_size=(35,20),
            option1text="Hide weights"
        )
        
        self.reset()

    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
        
        # Check if there is a new rendered graph
        new_surface = None
        if self.current_mwu:
            new_surface = self.MWU.get_new_graph_surface()
        else:
            new_surface = self.WM.get_new_graph_surface()
        if new_surface != None:
            self.elements["GRAPH_VIEW"].set_image(new_surface)
    
    def _handle_events(self, events):
        if self.auto_move and (get_time_milliseconds() - self.last_move_time > self.interval):
            self._roll_coin()
            
        for event in events:
            self.elements["HEADS_CHANCE_INPUT"].handleEvent(event)
            self.elements["ALPHA_INPUT"].handleEvent(event)
            self.elements["AUTO_INTERVAL_INPUT"].handleEvent(event)
            self.elements["MAX_T_INPUT"].handleEvent(event)
            self.elements["GRAPH_LIMIT_INPUT"].handleEvent(event)
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    self.reset()
                    return GAMESTATE.MENU
                elif self.elements["HEADS_CHANCE_INPUT"].is_hovered():
                    self.elements["HEADS_CHANCE_INPUT"].toggleSelected()
                elif self.elements["MAX_T_INPUT"].is_hovered():
                    self.elements["MAX_T_INPUT"].toggleSelected()
                elif self.elements["ALPHA_INPUT"].is_hovered():
                    self.elements["ALPHA_INPUT"].toggleSelected()
                elif self.elements["AUTO_INTERVAL_INPUT"].is_hovered():
                    self.elements["AUTO_INTERVAL_INPUT"].toggleSelected()
                elif self.elements["AUTO_TOGGLE"].is_hovered():
                    self.elements["AUTO_TOGGLE"].switch()
                    self._set_auto(self.elements["AUTO_TOGGLE"].state)
                elif self.elements["ROLL_BUTTON"].is_hovered():
                    self._roll_coin()
                elif self.elements["GRAPH_SWITCH"].is_hovered():
                    self.elements["GRAPH_SWITCH"].switch()
                    self.elements["GRAPH_VIEW"].clear()
                    self.current_mwu = not self.elements["GRAPH_SWITCH"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_LIMIT_INPUT"].is_hovered():
                    self.elements["GRAPH_LIMIT_INPUT"].toggleSelected()
                elif self.elements["GRAPH_EXPECTED_TOGGLE"].is_hovered():
                    self.elements["GRAPH_EXPECTED_TOGGLE"].switch()
                    self.show_graph_expected = not self.elements["GRAPH_EXPECTED_TOGGLE"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_BOUND_TOGGLE"].is_hovered():
                    self.elements["GRAPH_BOUND_TOGGLE"].switch()
                    self.show_graph_bound = not self.elements["GRAPH_BOUND_TOGGLE"].state
                    self._draw_current_graph()
                elif self.elements["GRAPH_WEIGHTS_TOGGLE"].is_hovered():
                    self.elements["GRAPH_WEIGHTS_TOGGLE"].switch()
                    self.show_graph_weights = not self.elements["GRAPH_WEIGHTS_TOGGLE"].state
                    self._draw_current_graph()
                
    def _set_heads_chance(self, value):
        self.heads_chance = value
    
    def _set_alpha(self, value):
        if (self.alpha == value):
            return
        self.alpha = value
        self.reset()    # Reset to load learners with new alpha

    def _set_max_time_horizon(self, value):
        if (self.max_time_horizon == value):
            return
        self.max_time_horizon = int(value)
        self.reset()    # Reset to load learners (regret trackers) with new max time horizon
    
    def _set_interval(self, value):
        self.interval = value
    
    def _set_auto(self, value):
        if (self.elements["AUTO_TOGGLE"].state != value):
            self.elements["AUTO_TOGGLE"].switch()
        self.auto_move = value
    
    def _set_timestep_limit(self, value):
        self.limit_graph_timesteps = int(value)
        self._draw_current_graph()
    
    def _draw_current_graph(self):
        if self.current_mwu:
            self.MWU.draw_graph(
                show_weights=self.show_graph_weights,
                show_bound=self.show_graph_bound,
                show_expected=self.show_graph_expected,
                size=(700, 500),
                limit_timesteps=self.limit_graph_timesteps
            )
        else:
            self.WM.draw_graph(
                show_weights=self.show_graph_weights,
                show_bound=self.show_graph_bound,
                show_expected=self.show_graph_expected,
                size=(700, 500),
                limit_timesteps=self.limit_graph_timesteps
            )
    
    def _roll_coin(self):
        if self.total_rolls > self.MWU.regret_tracker._max_t:
            self._set_auto(False)
            return
        
        normalized_heads_chance = self.heads_chance/100
        self.latest_roll = random.choices([face for face in COINFACE], weights=(1-normalized_heads_chance, normalized_heads_chance))[0]
        latest_roll_text = "HEADS" if self.latest_roll == COINFACE.HEADS else "TAILS"
        self.total_rolls += 1
        self.last_move_time = get_time_milliseconds()
        
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll: {latest_roll_text}")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        
        ## Update learners
        # MWU
        mwu_guess = self.MWU.play()
        mwu_guess_text = "HEADS" if mwu_guess == COINFACE.HEADS else "TAILS"
        self.MWU.update(self.latest_roll)
        self.elements["PREDICTION_MWU"].updateText(f"MWU Prediction: {mwu_guess_text}")
        # WM
        wm_guess = self.WM.play()
        wm_guess_text = "HEADS" if wm_guess == COINFACE.HEADS else "TAILS"
        self.WM.update(self.latest_roll)
        self.elements["PREDICTION_WM"].updateText(f"WM Prediction: {wm_guess_text}")
        # draw updated graph
        self._draw_current_graph()
        
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
        limit = 30
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
            regret_tracker=MWURegretTracker(len(self.experts), self.alpha, max_t=self.max_time_horizon),
            seed=42
        )
        self.WM = WeightedMajorityPlayer(
            experts=self.experts.values(),
            loss_computer=CFLoss(),
            moves_enum=COINFACE,
            alpha=self.alpha,
            regret_tracker=WeightedMajorityRegretTracker(len(self.experts), self.alpha, max_t=self.max_time_horizon)
        )
        
        # Reset UI
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll:")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        self.elements["HISTORY_VIEW"].update_contents()
        self.elements["GRAPH_VIEW"].clear()
