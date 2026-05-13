import pygame, os

# FONT_STYLE = "monocraft"
FONT_PATH = os.path.join(os.getcwd(), "fonts", "Monocraft.otf")
OTHER_FONT_PATH = "./src/fonts/Monocraft.otf"

existing = {}
def get_font(size) -> pygame.font.Font:
    exists = existing.get(size, None)
    if exists is None: 
        try:
            existing[size] = pygame.font.Font(FONT_PATH, size)
        except FileNotFoundError as e:
            try:
                existing[size] = pygame.font.Font(OTHER_FONT_PATH, size)
            except FileNotFoundError as e:
                existing[size] = pygame.font.SysFont("arial", size)
    return existing[size]
