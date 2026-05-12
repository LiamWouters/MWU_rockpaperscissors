import pygame
from .UIelement import UIelement

class TextLabel(UIelement):
    def __init__(self, 
                 pos: tuple[int,int], 
                 font,
                 size=(None, None), # Or tuple: (width, height) in pixels
                 text="",
                 colors={
                     "default": "#cccccc"
                 },
                 show_bounding_box=False):
        super().__init__(pos, size[0], size[1], show_bounding_box=show_bounding_box)
        
        self.font = font
        self.colors = colors
        self.text_raw = text
        
        # renders
        self.text = self.font.render(text, True, self.colors["default"])
        self.text_rect = self.text.get_rect(center=self.bounding_box.center)
        
        # dynamic resizing of bounding box
        if size[0] == None or size[1] == None:
            self.set_bounding_box_size(self.text_rect.width, self.text_rect.height)
    
    def _renderElement(self, screen):
        screen.blit(self.text, self.text_rect)
    
    def updateText(self, value):
        self.text = self.font.render(value, True, self.colors["default"])
        self.text_rect = self.text.get_rect(center=self.bounding_box.center)
        self.set_bounding_box_size(self.text_rect.width, self.text_rect.height) # Dynamic resizing
        
