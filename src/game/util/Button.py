# Inspired by: https://thepythoncode.com/article/make-a-button-using-pygame-in-python
#          and https://www.youtube.com/watch?v=GMBqjxcKogA
import pygame

class Button():
    def __init__(self, 
                 pos: tuple[int,int], 
                 width, 
                 height,
                 font,
                 text="",
                 image=None, # Optional
                 colors={
                     "default": "#cccccc",
                     "hover": "#555555"
                 }):
        self.x = pos[0]
        self.y = pos[1]
        self.width = width
        self.height = height
        self.font = font
        self.colors = colors
        self.text_raw = text
        self.text = self.font.render(text, True, self.colors["default"])
        self.image = image
        
        # renders
        self._image_rect = None
        if self.image: self._image_rect = self.image.get_rect(center=(self.x, self.y))
        self._text_rect = self.text.get_rect(center=(self.x, self.y))
    
    def draw(self, screen):
        self._update_color()
        if self.image and self._image_rect:
            screen.blit(self.image, self._image_rect)
        screen.blit(self.text, self._text_rect)
    
    def is_hovered(self):
        mousePos = pygame.mouse.get_pos()
        if self._text_rect.collidepoint(mousePos):
            return True
        return False
    
    def _update_color(self):
        mousePos = pygame.mouse.get_pos()
        if self._text_rect.collidepoint(mousePos):
            self.text = self.font.render(self.text_raw, True, self.colors.get("hover", "#ffffff"))
        else:
            self.text = self.font.render(self.text_raw, True, self.colors.get("default", "#ffffff"))
