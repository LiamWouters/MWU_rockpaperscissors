from game.GameRunner import GameRunner
from strategies.RandomExpert import RandomExpert

if __name__ == "__main__":
    print("Starting game...")
    game = GameRunner(
        experts={"random": RandomExpert()}
    )
    print("Finished game!")
