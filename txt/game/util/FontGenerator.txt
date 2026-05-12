import pygame

FONT_STYLE = "monocraft"
existing = {}
def get_font(size) -> pygame.font.Font:
    return existing.get(size, pygame.font.SysFont(FONT_STYLE, size))
