import pygame

class Branches(pygame.sprite.Sprite):
    def __init__(self, image_path, screen_width, screen_height):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)