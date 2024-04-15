import random
import pygame

class PheromoneTrail(pygame.sprite.Sprite):
    def __init__(self, position, lifespan=200):
        super().__init__()
        self.start_diameter = 4
        self.end_diameter = 1
        self.original_lifespan = lifespan
        self.lifespan = lifespan
        self.image = pygame.Surface((self.start_diameter*2, self.start_diameter*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=position)

    def update_image(self, diameter):
        fade_ratio = self.lifespan / self.original_lifespan
        alpha = int(128 * fade_ratio)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (128, 0, 128, alpha), (diameter, diameter), diameter)

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()
            return

        fade_ratio = self.lifespan / self.original_lifespan
        new_diameter = int(self.end_diameter + (self.start_diameter - self.end_diameter) * fade_ratio)

        self.update_image(new_diameter)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))