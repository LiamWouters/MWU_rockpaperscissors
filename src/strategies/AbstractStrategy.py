from abc import ABC, abstractmethod
from game import MOVES

class AbstractStrategy(ABC):
    
    @abstractmethod
    def play(gameHistory: list) -> MOVES:
        """
        Apply a strategy and return a move
        
        Arguments: 
            - gameHistory: A chronological list of previous games
        """
        pass
