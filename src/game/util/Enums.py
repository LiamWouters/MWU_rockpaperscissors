from enum import IntEnum, Enum

class GAMES(Enum):
    RPS="Rock-Paper-Scissors"
    CF="Coin-Flip"

class MOVES(IntEnum):
    ROCK = 0
    PAPER = 2
    SCISSORS = 1
    
class GAMESTATE(IntEnum):
    STOPPED = 0
    MENU = 1
    MANUAL = 2
    AUTO = 3
    
