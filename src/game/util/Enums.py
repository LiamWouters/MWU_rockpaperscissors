from enum import IntEnum, Enum

class GAMES(Enum):
    RPS="Rock-Paper-Scissors"
    CF="Coin-Flip"

class MOVES(IntEnum):
    ROCK = 0
    PAPER = 2
    SCISSORS = 1

class COINFACE(IntEnum):
    TAILS = 0
    HEADS = 1
    
class GAMESTATE(IntEnum):
    STOPPED = 0
    MENU = 1
    
    GENERATEINPUT = 2
    
    PLAYAUTORPS = 3
    PLAYAUTOCF = 4
    
    PLAYMANUALRPS = 5
