import pygame


class NumericInput:
    def __init__(self, screen, font, pos, min_value, max_value, step):
        self.screen = screen
        self.font = font
        self.pos = pos
        self.value = min_value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        value_text_width, value_text_height = font.size(str(max_value))
        self.rect = pygame.Rect(pos, (value_text_width + 10, value_text_height + 10))
        button_size = value_text_height + 10
        self.increase_button = pygame.Rect(self.rect.right + 5, self.rect.y, button_size, button_size)
        self.decrease_button = pygame.Rect(self.rect.left - button_size - 5, self.rect.y, button_size, button_size)

    def draw(self, offset):
        absolute_pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])
        self.rect.topleft = absolute_pos
        self.increase_button.topleft = (self.rect.right + 5, self.rect.y)
        self.decrease_button.topleft = (self.rect.left - self.decrease_button.width - 5, self.rect.y)
        
        label_text = self.font.render("Season Length (min):", True, (255, 255, 255))
        label_text_position = (self.decrease_button.left - label_text.get_width() - 10, 
                               self.rect.centery - label_text.get_height() / 2)
        
        self.screen.blit(label_text, label_text_position)
        text_surf = self.font.render(str(self.value), True, (255, 255, 255))
        self.screen.blit(text_surf, (self.rect.x + (self.rect.width - text_surf.get_width()) / 2, 
                                     self.rect.y + (self.rect.height - text_surf.get_height()) / 2))
        
        increase_text = self.font.render("+", True, (255, 255, 255))
        decrease_text = self.font.render("-", True, (255, 255, 255))
        self.screen.blit(increase_text, (self.increase_button.x + (self.increase_button.width - increase_text.get_width()) / 2, 
                                         self.increase_button.y + (self.increase_button.height - increase_text.get_height()) / 2))
        self.screen.blit(decrease_text, (self.decrease_button.x + (self.decrease_button.width - decrease_text.get_width()) / 2, 
                                         self.decrease_button.y + (self.decrease_button.height - decrease_text.get_height()) / 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.increase_button.collidepoint(event.pos) and self.value < self.max_value:
                self.value += self.step
            if self.decrease_button.collidepoint(event.pos) and self.value > self.min_value:
                self.value -= self.step

    def get_value(self):
        return self.value