import pygame
from .UIelement import UIelement

class NumberInput(UIelement):
    def __init__(self, 
                 pos: tuple[int,int], 
                 font,
                 size=(None, None), # Ignored
                 fixed_width=100,
                 upperLimit=None,   # inclusive lower limit (x): [x
                 lowerLimit=None,   # inclusive upper limit (y):   ,y]
                 callback=None,
                 start_text="template",
                 start_value=0.0,
                 colors={
                     "bg": "#333333",
                     "template": "#666666",
                     "locked_text": "#5684D8",
                     "text": "#ffffff"
                 },
                 show_bounding_box=False):
        self.font = font
        
        super().__init__(pos, fixed_width, self.font.get_linesize(), show_bounding_box=show_bounding_box)        
        
        self.colors = colors
        self.start_text = start_text
        self.callback = callback
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        
        self.selected = False
        self.confirmed_value = start_value
        self.value = self.start_text if self.confirmed_value == None else str(self.confirmed_value)
        
        self.updateText()
    
    def _renderElement(self, screen):
        pygame.draw.rect(screen, self.colors["bg"], self.bounding_box)
        screen.blit(self.value_text, self.value_rect)
        
    def updateText(self):
        color = self.colors["text"] if self.value != self.start_text else self.colors["template"]
        try:
            if not self.selected and float(self.value) == self.confirmed_value:
                color = self.colors["locked_text"]
        except:
            pass
        
        self.value_text = self.font.render(self.value, True, color)
        self.value_rect = self.value_text.get_rect()
        self.value_rect.left = self.bounding_box.left
        self.value_rect.top = self.bounding_box.top
        
    def toggleSelected(self):
        if not self.selected:
            if self.value == self.start_text:
                self.value = ""
        else:
            try:
                toConfirm = float(self.value) # Confirm if valid
                if (self.lowerLimit != None and toConfirm < self.lowerLimit):
                    raise ValueError(f"Invalid input: Under lower limit ({self.lowerLimit})")
                if (self.upperLimit != None and toConfirm > self.upperLimit):
                    raise ValueError(f"Invalid input: Over upper limit ({self.upperLimit})")
                self.confirmed_value = toConfirm
                if self.callback:
                    self.callback(self.confirmed_value)
            except ValueError as e:
                print(e)
                self.value = self.start_text
        
        self.selected = not self.selected
        self.updateText()
    
    def handleEvent(self, event):
        if event.type == pygame.KEYUP and self.selected:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN: # enter pressed
                self.toggleSelected()
            else:
                if event.unicode.isnumeric() or event.unicode in ['.', '-']:
                    self.value += event.unicode
        self.updateText()
        