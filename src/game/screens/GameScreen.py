import pygame
from abc import ABC, abstractmethod

black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

class GameScreen(ABC):
    def __init__(self, screen):
        self.screen = screen
    
    @abstractmethod
    def process(self, events):
        pass
