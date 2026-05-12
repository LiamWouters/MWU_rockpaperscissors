import pygame, os, random
from game.util import GAMESTATE, GAMES, COINFACE, get_font, Button, FileView, NumberInput, TextLabel
from .GameScreen import *

# TODO: have a bias NumberInput that makes the coin flip "unfair"
# TODO: on the fly generate a coin toss based on the bias
# TODO: store it to the "history" (file) 

CF_HISTORY_FILE_PATH = os.path.join(os.getcwd(), "CF_manual_history.txt")

class PlayAutoCF(GameScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.heads_chance = 50.0
        self.latest_roll = None
        self.total_rolls = 0
        
        # Create history file if it does not exist
        open(CF_HISTORY_FILE_PATH, 'w').close()
        
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
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 15/100),
            font=get_font(16),
            text="Set Heads Chance (%):"
        )
        self.elements["HEADS_CHANCE_INPUT"] = NumberInput(
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 18/100),
            font=get_font(16),
            fixed_width=135,
            callback=self._set_heads_chance,
            start_value=self.heads_chance,
            start_text="heads chance"
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
            show_bounding_box=True
        )
        self.elements["TOTAL_ROLLS"] = TextLabel(
            pos=(self.screen.get_width() * 25/100, self.screen.get_height() * 59/100),
            font=get_font(16),
            text=f"Total Rolls: {self.total_rolls}",
            show_bounding_box=True
        )

    def _draw(self):
        self.screen.blit(self.elements["TITLE_TEXT"], self.elements["TITLE_RECT"])
    
    def _handle_events(self, events):
        for event in events:
            self.elements["HEADS_CHANCE_INPUT"].handleEvent(event)
            if event.type == pygame.QUIT:
                return GAMESTATE.STOPPED
            if event.type == pygame.MOUSEBUTTONUP:
                if self.elements["BACK_BUTTON"].is_hovered():
                    self.reset()
                    return GAMESTATE.MENU
                elif self.elements["HEADS_CHANCE_INPUT"].is_hovered():
                    self.elements["HEADS_CHANCE_INPUT"].toggleSelected()
                elif self.elements["ROLL_BUTTON"].is_hovered():
                    self._roll_coin()
                
    def _set_heads_chance(self, value):
        self.heads_chance = value
        
    def _roll_coin(self):
        normalized_heads_chance = self.heads_chance/100
        self.latest_roll = random.choices([face.value for face in COINFACE], weights=(1-normalized_heads_chance, normalized_heads_chance))[0]
        self.total_rolls += 1
        
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll: {self.latest_roll}")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        
        # Store to history file
        with open(CF_HISTORY_FILE_PATH, 'a') as f: 
            f.write(f"{self.latest_roll},\n")
        self.elements["HISTORY_VIEW"].update_contents()

    def reset(self):
        # Reset values
        open(CF_HISTORY_FILE_PATH, 'w').close()
        self.latest_roll = None
        self.total_rolls = 0
        # Reset UI
        self.elements["LATEST_ROLL"].updateText(f"Latest Roll:")
        self.elements["TOTAL_ROLLS"].updateText(f"Total Rolls: {self.total_rolls}")
        self.elements["HISTORY_VIEW"].update_contents()
