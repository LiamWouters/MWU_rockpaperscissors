import pygame
from game.util import UIelement
from abc import ABC, abstractmethod

black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

class GameScreen(ABC):
    def __init__(self, screen):
        self.screen = screen
        
        self.elements = {}
    
    def process(self, events):
        self.screen.fill("#171c23")
        
        # Draw screen specific elements (UIelement inheritants are drawn seperately)
        self._draw()
        
        uielements = [e for _, e in self.elements.items() if isinstance(e, UIelement)]
        sorted_UIelements = sorted(uielements, key=lambda x: x.z_layer)
        
        ## Draw all UIelements
        for element in sorted_UIelements:
            element.draw(self.screen) 
        
        return self._handle_events(events)   
    
    @abstractmethod
    def _handle_events(self, events):
        pass
    
    @abstractmethod
    def _draw(self):
        pass
