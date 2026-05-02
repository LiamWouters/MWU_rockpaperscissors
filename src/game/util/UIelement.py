import pygame
from abc import ABC, abstractmethod

class UIelement(ABC):
    def __init__(self, pos, width, height, show_bounding_box=False):
        # For initialisation, if these are None they will be dynamically set based on child class
        if width == None: width = 75
        if height == None: height = 75
        self.bounding_box = pygame.Rect(0,0, width, height)
        self.bounding_box.center = (pos[0], pos[1])
        
        self.show_bounding_box = show_bounding_box
    
    @abstractmethod
    def _renderElement(self, screen) -> None:
        """ Child class renders its visual elements """
        pass
    
    def draw(self, screen) -> None:
        screen.set_clip(self.bounding_box) # Can only modify pixels in the bounding box
        
        self._renderElement(screen)
        
        if self.show_bounding_box:
            pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 1)
            
        screen.set_clip(None) # Can modify whole screen again
    
    def is_hovered(self) -> bool:
        return self.bounding_box.collidepoint(pygame.mouse.get_pos())
    
    def set_bounding_box_size(self, width, height, paddingx=10, paddingy=10):
        oldCenter = self.bounding_box.center
        self.bounding_box.width = width + paddingx
        self.bounding_box.height = height + paddingy
        self.bounding_box.center = oldCenter # recenter after changing size
