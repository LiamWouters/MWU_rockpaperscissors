import pygame
from abc import ABC, abstractmethod

class UIelement(ABC):
    def __init__(self, pos, width, height, show_bounding_box=False, show_bg=False, active=True, z_layer=1):
        # For initialisation, if these are None they will be dynamically set based on child class
        if width == None: width = 75
        if height == None: height = 75
        self.bounding_box = pygame.Rect(0,0, width, height)
        self.bounding_box.center = (pos[0], pos[1])
        
        self.show_bounding_box = show_bounding_box
        self.show_bg = show_bg
        self.active = active
        self.z_layer = z_layer
        
        self.bg_color = "#13171c"
        self.bg_border_color = "#30353e"
    
    @abstractmethod
    def _renderElement(self, screen) -> None:
        """ Child class renders its visual elements """
        pass
    
    def draw(self, screen) -> None:
        if not self.active: return
        screen.set_clip(self.bounding_box) # Can only modify pixels in the bounding box
        
        if self.show_bounding_box:
            pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 1)
        if self.show_bg:
            pygame.draw.rect(screen, self.bg_color, self.bounding_box, border_radius=10)
            pygame.draw.rect(screen, self.bg_border_color, self.bounding_box, width=1, border_radius=10)
        
        self._renderElement(screen)
            
        screen.set_clip(None) # Can modify whole screen again
    
    def is_hovered(self) -> bool:
        if not self.active: return False
        return self.bounding_box.collidepoint(pygame.mouse.get_pos())
    
    def set_bounding_box_size(self, width, height, paddingx=10, paddingy=10):
        oldCenter = self.bounding_box.center
        self.bounding_box.width = width + paddingx
        self.bounding_box.height = height + paddingy
        self.bounding_box.center = oldCenter # recenter after changing size
