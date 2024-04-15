import pygame

class TreeSap(pygame.sprite.Sprite):
    def __init__(self, color, diameter, lifespan, screen_width=None, screen_height=None, game_state = None):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.lifespan = lifespan
        self.color = color
        self.size = diameter
        
        self.game_state = game_state
        
        self.last_update_time = self.game_state.get_current_time()

        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (diameter // 2, diameter // 2), diameter // 2)

        self.rect = self.image.get_rect()

    def update(self):
        current_time = self.game_state.get_current_time()
        if current_time - self.last_update_time >= 1:
            self.lifespan -= 1
            self.last_update_time = current_time
            
            if self.lifespan <= 0:
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))