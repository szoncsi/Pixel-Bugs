import pygame
from info_panel.numeric_input import NumericInput

class InfoPanel:
    def __init__(self, screen, font, pos, size, bg_color=(0, 0, 0, 128), current_season = None, game_state = None):
        self.screen = screen
        self.font = font
        self.pos = pos
        self.size = size
        self.bg_color = bg_color
        self.visible = False   
        self.game_state = game_state
        self.start_time = self.game_state.get_current_time()
        self.current_season = current_season
        self.season_duration_minutes = 4
        self.season_count = 0
        self.season_duration_input_box = pygame.Rect(self.pos[0] + 10, self.pos[1] + 80, 140, 32)
        self.numeric_input = NumericInput(screen, font, (10, 40), 1, 10, 1)       
        self.is_paused = False
        
    def set_pause(self, is_paused):
        self.is_paused = is_paused
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.season_duration_input_box.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        self.numeric_input.handle_event(event)

    def toggle_visibility(self):
        self.visible = not self.visible
        
    def update_season(self, season):
        self.current_season = season
        
    def get_numeric_input_value(self):
        return self.numeric_input.get_value()
        
    def update_season_count(self, count):
        self.season_count = count
    
    def update_time_until_next_season(self, next_season_change):
        self.next_season_change = next_season_change

    def draw(self):
        if not self.visible:
            return
        
        s = pygame.Surface(self.size, pygame.SRCALPHA)
        s.fill(self.bg_color)
        self.screen.blit(s, self.pos)
        
        elapsed_time = int(self.game_state.get_elapsed_game_time())
        time_until_next_season = int(self.game_state.get_time_until_next_season())
        elapsed_since_last_season_change = int(self.game_state.get_elapsed_since_last_season_change())
        
        progress = round(self.game_state.get_progress() * 100)
            
        time_text = self.font.render(f"Elapsed Game Time: {elapsed_time}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.pos[0] + 10, self.pos[1] + 10))
        
        if self.current_season:
            season_text = self.font.render(f"Current Season: {self.current_season.name}", True, (255, 255, 255))
            self.screen.blit(season_text, (self.pos[0] + 10, self.pos[1] + 30))
        
        elapsed_time_text = self.font.render(f"Elapsed Since Last Season: {elapsed_since_last_season_change}s", True, (255, 255, 255))
        self.screen.blit(elapsed_time_text, (self.pos[0] + 10, self.pos[1] + 70))

        season_count_text = self.font.render(f"Seasons Passed: {self.season_count}", True, (255, 255, 255))
        self.screen.blit(season_count_text, (self.pos[0] + 10, self.pos[1] + 90))
        
        self.numeric_input.draw((self.pos[0] + 206, self.pos[1] + 65))
        
        remaining_time_text = self.font.render(f"Time Until Next Season: {int(time_until_next_season)}s", True, (255, 255, 255))
        self.screen.blit(remaining_time_text, (self.pos[0] + 10, self.pos[1] + 50))

        progress_text = self.font.render(f"Season Progress: {progress}%", True, (255, 255, 255))
        self.screen.blit(progress_text, (self.pos[0] + 10, self.pos[1] + 128))

