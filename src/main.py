from game.GameRunner import GameRunner
from game.util import MOVES, COINFACE
from strategies import (
    BeatLastHumanExpert,
    CopycatLastHumanExpert,
    FirstRandomThenFixedExpert,
    RandomExpert,
)

if __name__ == "__main__":
    print("Starting game...")
    game = GameRunner(
        expertsRPS={
            "always_random": RandomExpert(MOVES, seed=0),
            "first_random_then_fixed": FirstRandomThenFixedExpert(seed=1),
            "copycat_last_human": CopycatLastHumanExpert(seed=2),
            "beat_last_human": BeatLastHumanExpert(seed=3),
        },
        expertsCF={
            "always_random": RandomExpert(COINFACE, seed=0),
        }
    )
    print("Finished game!")
