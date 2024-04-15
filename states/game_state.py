import math
import random
import sys
import pygame
from info_panel.bug_info_panel import BugInfoPanel
from pixels.factories.food_factory import FoodFactory
from pixels.tree_crown import TreeCrown
from track import Track
from info_panel.info_panel import InfoPanel
from states.season_state import SeasonState
from info_panel.numeric_input import NumericInput
from pixels.branches import Branches
from pixels.tree_sap import TreeSap
from pixels.bug import Bug
import time
from pixels.factories.bug_factory import BugFactory

class GameState:
    
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.brown = (165, 42, 42)
        self.zoom_level = 1.0
        self.zoom_center = (self.screen_width // 2, self.screen_height // 2)
        self.is_dragging = False
        self.start_drag_pos = (0, 0)
        self.is_game_active = True
        self.request_restart = False
        self.is_paused = False
        self.elapsed_game_time = None
        self.game_time = None
        self.actual_start_time = time.time()
        self.accumulated_pause_time = 0
        self.pause_start_time = None
        self.elapsed_time_since_last_season_change = None
        self.progress = 0
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pixel Bugs")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.numeric_input = NumericInput(self.screen, self.font, (10, 10), 1, 10, 1)
        self.current_season = SeasonState.SPRING
        self.season_change_interval = 60 
        self.last_season_change = self.get_current_time()
        self.next_season_change = self.get_current_time() + self.season_change_interval
        self.season_count = 0
        self.petal_update_interval_base = 1
        self.petal_update_interval = self.petal_update_interval_base
        self.info_panel = InfoPanel(self.screen, self.font, (10, 10), (300, 150), current_season=self.current_season, game_state=self)
        self.bug_info_panel = BugInfoPanel(self.screen, self.font, (self.screen_width - 310, 10), (300, 210))
        self.track = Track('pics/track.png', self.screen_width, self.screen_height)
        self.branches = Branches('pics/branches.png', self.screen_width, self.screen_height)
        self.bug_list = pygame.sprite.Group()
        self.pupa_list = []
        self.tree_sap_list = pygame.sprite.Group()
        self.next_tree_sap_add_time = self.get_current_time() + random.randint(5, 10)
        self.max_tree_sap_groups = 10
        self.tree_crown = TreeCrown('pics/tree_crown.png', self.screen_width, self.screen_height, self)  
        self.play_button_image = pygame.image.load('pics/start.png').convert_alpha()
        self.pause_button_image = pygame.image.load('pics/pause.png').convert_alpha()
        self.stop_button_image = pygame.image.load('pics/stop.png').convert_alpha()
        self.pause_button_rect = self.pause_button_image.get_rect(center=(self.screen_width // 2 - 50, 50))
        self.play_button_rect = self.play_button_image.get_rect(center=(self.screen_width // 2 - 50, 50))
        self.stop_button_rect = self.stop_button_image.get_rect(center=(self.screen_width // 2 + 50, 50))
        self.stop_button_rect = self.stop_button_image.get_rect()
        self.stop_button_rect.bottomright = (self.screen_width - 10, self.screen_height - 10)
        self.pause_button_rect = self.pause_button_image.get_rect()
        self.pause_button_rect.bottomright = (self.stop_button_rect.left - 10, self.screen_height - 10)
        self.play_button_rect = self.pause_button_image.get_rect()
        self.play_button_rect.bottomright = (self.stop_button_rect.left - 10, self.screen_height - 10)
        self.pheromone_trails = pygame.sprite.Group()
    
    def initialize(self):
        self.zoom_level = 1.0
        self.zoom_center = (self.screen_width // 2, self.screen_height // 2)
        self.is_dragging = False
        self.start_drag_pos = (0, 0)
        
        self.bug_list.empty()
        self.tree_sap_list.empty()
        
        self.create_bugs()
        self.create_tree_sap()
        
    def create_bugs(self):
        bug_factory = BugFactory()
        traversable_positions = self.track.get_traversable_positions()
        for _ in range(20):
            if not traversable_positions:
                break
            grid_x, grid_y = random.choice(traversable_positions)
            x, y = self.track.grid_to_pixel_position((grid_x, grid_y))
            bug = bug_factory.create_pixel(self.white, 2, 2, self.screen_width, self.screen_height, self, block_size=1)
            bug.rect.x = x
            bug.rect.y = y
            self.bug_list.add(bug)
    
    def spawn_pupa(self):
        for pupa_attributes in self.pupa_list:
            if pupa_attributes is None:
                continue
            traversable_positions = self.track.get_traversable_positions()
            if not traversable_positions:
                break

            grid_x, grid_y = random.choice(traversable_positions)
            x, y = self.track.grid_to_pixel_position((grid_x, grid_y))
            
            if isinstance(pupa_attributes, dict):
                new_bug = Bug(width=2, height=2, screen_width=self.screen_width, screen_height=self.screen_height, game_state=self, block_size=1, **pupa_attributes)
                new_bug.rect.x = x
                new_bug.rect.y = y
                self.bug_list.add(new_bug)
            else:
                print("Invalid pupa attributes found:", pupa_attributes)

        self.pupa_list = []
                    
    def create_tree_sap(self):
        food_factory = FoodFactory()
        traversable_positions = self.track.get_traversable_positions()

        for _ in range(random.randint(1, self.max_tree_sap_groups)):
            if not traversable_positions:
                break

            for _ in range(random.randint(2, 12)):
                if not traversable_positions:
                    break

                grid_pos = random.choice(traversable_positions)
                traversable_positions.remove(grid_pos)

                center_x, center_y = self.track.grid_to_pixel_position(grid_pos)

                diameter = random.randint(2, 6)
                lifespan = random.randint(10, 20)

                tree_sap = food_factory.create_pixel((255, 165, 0), diameter, lifespan, self.screen_width, self.screen_height, game_state=self)
                tree_sap.rect.x = center_x - diameter // 2
                tree_sap.rect.y = center_y - diameter // 2
                self.tree_sap_list.add(tree_sap)

    def handle_events(self):     
        for event in pygame.event.get():
            self.info_panel.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    if self.pause_button_rect.collidepoint(event.pos) and not self.is_paused:
                        self.is_paused = True
                        self.pause_start_time = time.time()
                    elif self.play_button_rect.collidepoint(event.pos) and self.is_paused:
                        self.is_paused = False

                        if self.pause_start_time:
                            self.accumulated_pause_time += (time.time() - self.pause_start_time)
                        self.pause_start_time = None
                    elif self.stop_button_rect.collidepoint(event.pos):
                        self.restart_game_request()
                        return
                    
                    zoomed_click_x = (event.pos[0] - (self.zoom_center[0] - self.screen_width / 2 * self.zoom_level)) / self.zoom_level
                    zoomed_click_y = (event.pos[1] - (self.zoom_center[1] - self.screen_height / 2 * self.zoom_level)) / self.zoom_level
                    zoomed_click_pos = (zoomed_click_x, zoomed_click_y)

                    for bug in self.bug_list:
                        if bug.rect.collidepoint(zoomed_click_pos):
                            self.bug_info_panel.set_selected_bug(bug)
                            break
                    else:
                        self.bug_info_panel.set_selected_bug(None)
                elif event.button == 3:
                    self.is_dragging = True
                    self.start_drag_pos = event.pos
                elif event.button == 4:
                    self.zoom_level *= 1.1
                elif event.button == 5:
                    self.zoom_level /= 1.1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.is_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    current_pos = event.pos
                    dx = current_pos[0] - self.start_drag_pos[0]
                    dy = current_pos[1] - self.start_drag_pos[1]
                    self.zoom_center = (self.zoom_center[0] + dx, self.zoom_center[1] + dy)
                    self.start_drag_pos = current_pos
                
                zoomed_mouse_x = (event.pos[0] - (self.zoom_center[0] - self.screen_width / 2 * self.zoom_level)) / self.zoom_level
                zoomed_mouse_y = (event.pos[1] - (self.zoom_center[1] - self.screen_height / 2 * self.zoom_level)) / self.zoom_level
                zoomed_mouse_pos = (zoomed_mouse_x, zoomed_mouse_y)

                cursor_over_bug = False
                for bug in self.bug_list:
                    if bug.rect.collidepoint(zoomed_mouse_pos):
                        cursor_over_bug = True
                        break

                cursor_over_button = self.pause_button_rect.collidepoint(event.pos) or \
                                    self.play_button_rect.collidepoint(event.pos) or \
                                    self.stop_button_rect.collidepoint(event.pos)

                if cursor_over_bug or cursor_over_button:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.info_panel.toggle_visibility()
                    
    def get_current_time(self):
        if self.is_paused:
            return self.pause_start_time - self.accumulated_pause_time
        else:
            return time.time() - self.accumulated_pause_time
    
    def get_elapsed_game_time(self):
        return self.elapsed_game_time

    def get_time_until_next_season(self):
        return max(0, self.next_season_change - self.get_current_time())
          
    def get_elapsed_since_last_season_change(self):
        return self.get_current_time() - self.last_season_change
    
    def get_progress(self):
        return self.progress

    def update(self):
        
        if self.is_paused:
            self.info_panel.set_pause(True)
            return
        else:
            self.info_panel.set_pause(False)
            
        current_time = self.get_current_time()
            
        self.elapsed_game_time = current_time - self.actual_start_time
        
        season_length_in_minutes = self.info_panel.get_numeric_input_value()
        season_length_in_seconds = season_length_in_minutes * 60

        self.petal_update_interval = self.petal_update_interval_base * (2 ** (season_length_in_minutes - 1))
        
        self.tree_crown.set_petal_update_interval(self.petal_update_interval)
        
        elapsed_time = current_time - self.last_season_change

        if season_length_in_seconds != self.season_change_interval:
            self.season_change_interval = season_length_in_seconds

            if elapsed_time >= season_length_in_seconds:
                self.next_season_change = current_time
            else:
                self.next_season_change = current_time + (season_length_in_seconds - elapsed_time)

        if current_time >= self.next_season_change:
            self.current_season = SeasonState((self.current_season.value % len(SeasonState)) + 1)
            self.last_season_change = current_time
            self.next_season_change = current_time + self.season_change_interval
            self.season_count += 1

            for bug in list(self.bug_list):
                bug.lifespan -= 1
                if bug.lifespan <= 0:
                    bug.kill()
            
            if self.current_season == SeasonState.SPRING:
                self.spawn_pupa()

            self.info_panel.update_season(self.current_season)
            self.info_panel.update_season_count(self.season_count)

            progress = 0
        else:
            elapsed_time_since_last_season_change = current_time - self.last_season_change
            progress = elapsed_time_since_last_season_change / self.season_change_interval
            progress = min(1, progress)
            
        self.progress = progress
        
        self.tree_crown.update(progress, self.current_season.name, self.season_change_interval)
            
        for bug in self.bug_list:
            bug.update()
        
        if current_time >= self.next_tree_sap_add_time:
            current_groups = len(self.tree_sap_list) // 6
            if current_groups < self.max_tree_sap_groups:
                self.create_tree_sap()
                self.next_tree_sap_add_time = current_time + random.randint(5, 10)

        for tree_sap in self.tree_sap_list:
            tree_sap.update()
            if tree_sap.lifespan <= 0:
                tree_sap.kill()
                
        for trail in self.pheromone_trails:
            trail.update()

    def draw(self):
        self.screen.fill(self.black)
        temp_surface = pygame.Surface((self.screen_width, self.screen_height))
        temp_surface.fill(self.black)  
        self.branches.draw(temp_surface)
        self.tree_crown.draw(temp_surface, self.current_season.name)

        for trail in self.pheromone_trails:
            trail.draw(temp_surface)
        for tree_sap in self.tree_sap_list:
            tree_sap.draw(temp_surface)
        for bug in self.bug_list:
            bug.draw(temp_surface)
        
        zoomed_surface = pygame.transform.smoothscale(temp_surface, 
                        (int(self.screen_width * self.zoom_level), int(self.screen_height * self.zoom_level)))

        zoomed_rect = zoomed_surface.get_rect(center=self.zoom_center)

        self.screen.blit(zoomed_surface, zoomed_rect.topleft)
        
        self.info_panel.draw()
        self.bug_info_panel.draw()
        
        self.draw_buttons()

        pygame.display.flip()
        
    def draw_buttons(self):
        if self.is_paused:
            self.screen.blit(self.play_button_image, self.play_button_rect.topleft)
        else:
            self.screen.blit(self.pause_button_image, self.pause_button_rect.topleft)
        self.screen.blit(self.stop_button_image, self.stop_button_rect.topleft)
        
    def restart_game_request(self):
        self.request_restart = True