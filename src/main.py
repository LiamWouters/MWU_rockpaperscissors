from game.GameRunner import GameRunner
from strategies import (
    BeatLastHumanExpert,
    CopycatLastHumanExpert,
    FirstRandomThenFixedExpert,
    RandomExpert,
)

if __name__ == "__main__":
    print("Starting game...")
    game = GameRunner(
        experts={
            "always_random": RandomExpert(seed=0),
            "first_random_then_fixed": FirstRandomThenFixedExpert(seed=1),
            "copycat_last_human": CopycatLastHumanExpert(seed=2),
            "beat_last_human": BeatLastHumanExpert(seed=3),
        }
    )
    print("Finished game!")
