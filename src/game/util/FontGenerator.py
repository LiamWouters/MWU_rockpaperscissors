import pygame

FONT_STYLE = "monocraft"
existing = {}
def get_font(size) -> pygame.font.Font:
    exists = existing.get(size, None)
    if exists is None: existing[size] = pygame.font.SysFont(FONT_STYLE, size)
    return existing[size]
