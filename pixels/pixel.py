import pygame

class Pixel(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.blocks = []
        self.rect = pygame.Rect(0, 0, width, height)