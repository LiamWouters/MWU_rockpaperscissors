from game.RockPaperScissors import RPS
from strategies.RandomExpert import RandomExpert

if __name__ == "__main__":
    print("Starting game...")
    game = RPS(
        experts={"random": RandomExpert}
    )
    print("Finished game!")
