import pygame
import sys
from states.game_state import GameState


class StateManager:
    def __init__(self, screen):
        self.screen = screen
        self.is_game_active = False
        self.game_state = None
        self.start_button_image = pygame.image.load('pics/bug_icon_seasons.png').convert_alpha()
        self.start_button_rect = self.start_button_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        
    def show_start_screen(self):
        self.is_game_active = False
        button_rect = pygame.Rect(self.screen.get_width() // 2 - 50, self.screen.get_height() // 2 - 25, 100, 50)
        
        font = pygame.font.SysFont(None, 24)
        text = font.render("START Pixel Bugs", True, pygame.Color('white'))
        text_rect = text.get_rect(center=(self.start_button_rect.centerx, self.start_button_rect.bottom + 20))

        while not self.is_game_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                    self.is_game_active = True
                    self.game_state = GameState()
                    self.run_game()                   
                elif event.type == pygame.MOUSEMOTION:
                    if self.start_button_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.start_button_image, self.start_button_rect.topleft)
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.Clock().tick(30)

    def run_game(self):
        self.game_state.initialize()
        while self.is_game_active:
            self.game_state.handle_events()
            self.game_state.update()
            self.game_state.draw()
            if self.game_state.request_restart:
                self.show_start_screen()
                return
            pygame.time.Clock().tick(30)

def main():
    pygame.init()
    
    icon = pygame.image.load('pics/bug_icon_color.png')
    pygame.display.set_icon(icon)
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pixel Bugs")
    state_manager = StateManager(screen)

    state_manager.show_start_screen()
    state_manager.run_game()

if __name__ == "__main__":
    main()
    #cProfile.run('main()', 'profile_output')