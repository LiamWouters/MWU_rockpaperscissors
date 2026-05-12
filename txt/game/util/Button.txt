import pygame
from .UIelement import UIelement

class Button(UIelement):
    def __init__(self, 
                 pos: tuple[int,int], 
                 font,
                 size=(None, None), # Or tuple: (width, height) in pixels
                 text="",
                 image=None, # Optional
                 colors={
                     "default": "#cccccc",
                     "hover": "#555555"
                 },
                 show_bounding_box=False):
        super().__init__(pos, size[0], size[1], show_bounding_box=show_bounding_box)
        
        self.font = font
        self.colors = colors
        self.text_raw = text
        self.image = image
        
        # renders
        self._image_rect = None
        if self.image: self._image_rect = self.image.get_rect(center=(self.x, self.y))
        
        self.text = self.font.render(text, True, self.colors["default"])
        self._text_rect = self.text.get_rect(center=self.bounding_box.center)
        
        # dynamic resizing of bounding box
        if size[0] == None or size[1] == None:
            self.set_bounding_box_size(self._text_rect.width, self._text_rect.height)
    
    def _renderElement(self, screen):
        self._update_color()
        if self.image and self._image_rect:
            screen.blit(self.image, self._image_rect)
        screen.blit(self.text, self._text_rect)
    
    def _update_color(self):
        mousePos = pygame.mouse.get_pos()
        if self._text_rect.collidepoint(mousePos):
            self.text = self.font.render(self.text_raw, True, self.colors.get("hover", "#ffffff"))
        else:
            self.text = self.font.render(self.text_raw, True, self.colors.get("default", "#ffffff"))
