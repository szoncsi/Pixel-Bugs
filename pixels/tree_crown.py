import pygame
import numpy as np
import random
import time

class TreeCrown(pygame.sprite.Sprite):
    def __init__(self, image_path, screen_width, screen_height, game_state):
        super().__init__()
        
        self.game_state = game_state
        
        self.first_leaf_count_output = False
        self.second_leaf_count_output = False
        self.third_leaf_count_output = False
        
        self.snow_image = pygame.image.load('pics/snow.png').convert_alpha()
        self.snow_positions = self.get_snow_positions()
        self.snow_piles = {}
        
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.original_image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.image_cache = {}
        self.last_pink_update = self.game_state.get_current_time()
        self.pink_added_since_last_delay = 0
        self.pink_to_add = []
        self.pink_petals = set()
        self.flower_centers = set()
        self.processed_image = None
        self.petal_update_interval = 1
        self.last_flower_center_update = self.game_state.get_current_time()
        self.flower_center_addition_interval = 0.5
        self.flower_centers_to_add = 1
        
        self.last_green_update = self.game_state.get_current_time()
        self.green_addition_interval = 1.0 
        self.leaves = []
        
        self.leaf_color_transition_progress = 0
        self.last_color_update_time = self.game_state.get_current_time()
        self.last_update_time = self.game_state.get_current_time()
        
        self.snow_fall = 0
        self.snow_time = False
        self.snowing = False
        self.last_snow_update = self.game_state.get_current_time()
        self.snow_fall_rate = 0.05 
        self.last_snow_pile_addition_time = self.game_state.get_current_time()
        self.snow_pile_addition_rate = 0.5
        self.melting_batch_size = 10
        self.max_melting_batch_size = 40000
        self.melting_growth_factor = 1.1
        
        self.leaves_turning_into_yellow = False
        self.autumn_started = False
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.last_flower_center_addition_time = self.game_state.get_current_time()
        
        self.enough_flower_center_drawn = False
        self.all_pink_petals = set()
        
        self.MAX_FLOWER_CENTERS = 2000
        
        self.MAX_GREEN_LEAVES = 4000
        
        self.MAX_SNOW_PILED = 40000
        
        self.season_change_interval = 60
        
        self.yellow_shades = [
            (255, 255, 0),
            (255, 200, 0), 
            (255, 165, 0), 
        ]
        
        for leaf in self.leaves:
            leaf["final_color"] = random.choice(self.yellow_shades)
            leaf["color_changed"] = False
        
        self.red_pixel_coordinates = []
        for y in range(self.original_image.get_height()):
            for x in range(self.original_image.get_width()):
                if self.is_red(self.original_image.get_at((x, y))):
                    self.red_pixel_coordinates.append((x, y))
    
    def update(self, progress, season, season_change_interval):
        current_time = self.game_state.get_current_time()
        self.season_change_interval = season_change_interval
        progress_step = round(progress * 2) / 2
        cache_key = f"{season}_{progress_step}"

        if cache_key not in self.image_cache:
            self.process_tree_crown_background(season, progress_step)
        
        self.image = self.image_cache[cache_key]
        self.processed_image = self.image
        
        match season:
            case "SPRING":
                self.update_spring(progress, current_time, season)
            case "SUMMER":
                self.update_summer(progress, season)
            case "AUTUMN":
                self.update_autumn(progress, current_time, season)
            case "WINTER":
                self.update_winter(progress, current_time, season)          

    def process_tree_crown_background(self, season, progress_step):
        self.image_cache[f"{season}_{progress_step}"] = self.original_image
    
    def update_spring(self, progress, current_time, season):
        self.snow_time = False
        if progress < 0.6:
            if current_time - self.last_flower_center_update >= self.petal_update_interval:
                self.add_flower_centers(self.screen_width, self.screen_height)
                self.last_flower_center_update = current_time
                
            if current_time - self.last_pink_update >= self.petal_update_interval:
                self.add_pink_petals()
                self.last_pink_update = current_time
        else:
            self.remove_flower_centers(progress)
            self.remove_pink_petals(progress)
            self.add_leaves(progress, season)

    def update_summer(self, progress, season):
        self.remove_all_flower_center_and_pink()
        self.add_leaves(progress, season)

    def update_autumn(self, progress, current_time, season):
        if not self.autumn_started:
            self.last_color_update_time = self.game_state.get_current_time()
            self.autumn_started = True
        
        self.add_leaves(progress, season)             
        if self.leaves_turning_into_yellow == True:
            self.update_leaf_colors_for_fall()
            self.last_update_time = current_time   
            if progress > 0.8:
                self.remove_leaves(progress, season)

    def update_winter(self, progress, current_time, season):
        self.leaf_color_transition_progress = 0
        self.autumn_started = False
        self.leaves_turning_into_yellow = False
        snow_start_progress_rate = 0
        
        if self.leaves:
            self.remove_leaves(progress, season)
        elif progress > 0.1:
            current_time = self.game_state.get_current_time()
            delta_time = current_time - self.last_snow_update
            self.last_snow_update = current_time
            
            if self.snow_time == False:
                snow_start_progress_rate = progress
                self.snow_time = True
                self.snowing = True
            
            if self.snowing:
                if snow_start_progress_rate + 0.2 < progress:
                    self.add_snow_pile(current_time)             
                if progress <= 0.7:
                    self.snow_fall += self.snow_fall_rate * delta_time
                else:      
                    self.snow_fall -= 0.1
                    if self.snow_fall < 0:
                        self.snow_fall = 0
                        self.snowing = False
            else:
                self.melt_snow(delta_time)
    
    def add_snow_pile(self, current_time):
        total_snow_piled = sum(self.snow_piles.values())
        if total_snow_piled < self.MAX_SNOW_PILED and (current_time - self.last_snow_pile_addition_time) >= self.snow_pile_addition_rate:
            for _ in range(min(100, self.MAX_SNOW_PILED - total_snow_piled)):
                pos = random.choice(self.snow_positions)
                if pos not in self.snow_piles:
                    self.snow_piles[pos] = random.randint(1, 2)
                else:
                    self.snow_piles[pos] = min(self.snow_piles[pos] + random.randint(1, 2), 3)
            self.last_snow_pile_addition_time = current_time
            self.snow_pile_addition_rate *= 0.8

    def melt_snow(self, delta_time):
        total_melt_amount = self.melting_batch_size * delta_time

        while total_melt_amount > 0 and self.snow_piles:
            for pos in list(self.snow_piles.keys()):
                if total_melt_amount <= 0:
                    break

                melt_amount = min(total_melt_amount, self.snow_piles[pos])
                self.snow_piles[pos] -= melt_amount
                total_melt_amount -= melt_amount

                if self.snow_piles[pos] <= 0:
                    del self.snow_piles[pos]

        self.melting_batch_size = min(self.melting_batch_size + (self.max_melting_batch_size * 0.005), self.max_melting_batch_size)


    def is_red(self, color):
        r, g, b, _ = color
        return r > 150 and g < 50 and b < 50

    def draw(self, screen, season): 
        match season:
            case "SPRING":
                self.draw_spring(screen)

            case "SUMMER":
                self.draw_summer(screen)

            case "AUTUMN":
                self.draw_autumn(screen)

            case "WINTER":
                self.draw_winter(screen)
    
    def draw_spring(self, screen):
        for center in self.flower_centers:
            pygame.draw.circle(screen, (255, 182, 193), center, 2)

        for petal_pos in self.all_pink_petals:
            pygame.draw.circle(screen, (255, 20, 147), petal_pos, 2)
                    
        for leaf in self.leaves:
            if leaf["type"] == "circle":
                pygame.draw.circle(screen, leaf["color"], leaf["position"], leaf["radius"])                  
            else:                 
                leaf_surface = pygame.Surface((leaf["width"] * 2, leaf["height"] * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surface, leaf["color"], [0, 0, leaf["width"] * 2, leaf["height"] * 2])
                rotated_leaf = pygame.transform.rotate(leaf_surface, leaf["angle"])
                leaf_rect = rotated_leaf.get_rect(center=leaf["position"])
                screen.blit(rotated_leaf, leaf_rect.topleft)

    def draw_summer(self, screen):
        for leaf in self.leaves:
            if leaf["type"] == "circle":
                pygame.draw.circle(screen, leaf["color"], leaf["position"], leaf["radius"])
            else:
                leaf_surface = pygame.Surface((leaf["width"] * 2, leaf["height"] * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surface, leaf["color"], [0, 0, leaf["width"] * 2, leaf["height"] * 2])
                rotated_leaf = pygame.transform.rotate(leaf_surface, leaf["angle"])
                leaf_rect = rotated_leaf.get_rect(center=leaf["position"])
                screen.blit(rotated_leaf, leaf_rect.topleft)

    def draw_autumn(self, screen):
        for leaf in self.leaves:
            leaf_surface = pygame.Surface((leaf["width"] * 2, leaf["height"] * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, leaf["color"], [0, 0, leaf["width"] * 2, leaf["height"] * 2])
            rotated_leaf = pygame.transform.rotate(leaf_surface, leaf["angle"])
            leaf_rect = rotated_leaf.get_rect(center=leaf["position"])
            screen.blit(rotated_leaf, leaf_rect.topleft)

    def draw_winter(self, screen):
        snow_color = (255, 255, 255)
        for pos, amount in self.snow_piles.items():
            pygame.draw.circle(screen, snow_color, pos, min(5, amount))
        
        for _ in range(int(self.snow_fall)):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            pygame.draw.circle(screen, snow_color, (x, y), 2)

        for leaf in self.leaves:
            leaf_surface = pygame.Surface((leaf["width"] * 2, leaf["height"] * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, leaf["color"], [0, 0, leaf["width"] * 2, leaf["height"] * 2])
            rotated_leaf = pygame.transform.rotate(leaf_surface, leaf["angle"])
            leaf_rect = rotated_leaf.get_rect(center=leaf["position"])
            screen.blit(rotated_leaf, leaf_rect.topleft)
    
    def set_petal_update_interval(self, interval):
        self.petal_update_interval = interval
    
    def is_pink_at(self, x, y):
        if self.processed_image and 0 <= x < self.processed_image.get_width() and 0 <= y < self.processed_image.get_height():
            return self.processed_image.get_at((x, y)) == (255, 20, 147, 255)
        return False

    def add_pink_at(self, x, y):
        if self.processed_image and 0 <= x < self.processed_image.get_width() and 0 <= y < self.processed_image.get_height():
            self.processed_image.set_at((x, y), (255, 20, 147, 255))
            self.pink_petals.add((x, y))

    def add_pink_petals(self):
        if not self.enough_flower_center_drawn and len(self.flower_centers) >= self.MAX_FLOWER_CENTERS / 2:
            self.enough_flower_center_drawn = True
        if self.enough_flower_center_drawn:
            petals_to_add = 200
            
            if len(self.all_pink_petals) >= len(self.flower_centers) // 4:
                petals_to_add *= 2
                
            if len(self.all_pink_petals) >= len(self.flower_centers) // 2:
                petals_to_add *= 4

            flower_centers_list = list(self.flower_centers)
            for _ in range(petals_to_add):
                center = random.choice(flower_centers_list)
                x, y = center
                dx, dy = random.choice([(-3, 0), (3, 0), (0, -3), (0, 3)])
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.screen_width and 0 <= ny < self.screen_height and not self.is_pink_at(nx, ny) and (nx, ny) not in self.flower_centers:
                    self.add_pink_at(nx, ny)
                    self.all_pink_petals.add((nx, ny))

    def add_flower_centers(self, screen_width, screen_height):
        current_time = self.game_state.get_current_time()
        if len(self.flower_centers) < self.MAX_FLOWER_CENTERS and current_time - self.last_flower_center_addition_time >= self.flower_center_addition_interval:

            batch_size = min(300, self.MAX_FLOWER_CENTERS - len(self.flower_centers))
            max_x = screen_width - 1
            max_y = screen_height - 1
            batch_points = []
            for _ in range(batch_size):
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                if self.is_red(self.original_image.get_at((x, y))) and not self.is_flower_center_at(x, y):
                    batch_points.append((x, y))

            for point in batch_points:
                x, y = point
                self.processed_image.set_at((x, y), (255, 182, 193))
                self.flower_centers.add((x, y))

            self.last_flower_center_addition_time = current_time
    
    def is_flower_center_at(self, x, y):
        if self.processed_image and 0 <= x < self.processed_image.get_width() and 0 <= y < self.processed_image.get_height():
            return self.processed_image.set_at((x, y), (255, 182, 193)) 
        return False
    
    def remove_flower_centers(self, progress):
        if progress > 0.6:
            fade_factor = (progress - 0.6) * 0.05
            to_remove_flower_center = {center for center in self.flower_centers if random.random() < fade_factor}
            self.flower_centers -= to_remove_flower_center
            
    def remove_pink_petals(self, progress):
        if progress > 0.6:
            fade_factor = (progress - 0.6) * 0.05
            to_remove_pink = {petal for petal in self.pink_petals if random.random() < fade_factor}
            self.pink_petals -= to_remove_pink
            self.all_pink_petals -= to_remove_pink 
            
    def remove_all_flower_center_and_pink(self):
        self.flower_centers.clear()
        self.pink_petals.clear()
        self.all_pink_petals.clear()
        self.enough_flower_center_drawn = False
    
    def add_leaves(self, progress, current_season):
        current_time = self.game_state.get_current_time()
        if current_time - self.last_green_update < self.green_addition_interval:
            return

        green_shades = [(0, 155, 0), (0, 175, 0), (0, 195, 0), (0, 215, 0), (0, 235, 0)]
        batch_size = 100 if current_season == 'SPRING' else 400
        
        leaves_to_add = min(self.MAX_GREEN_LEAVES - len(self.leaves), batch_size)

        if current_season == 'SPRING':
            for _ in range(leaves_to_add):
                x = random.randint(0, self.original_image.get_width() - 1)
                y = random.randint(0, self.original_image.get_height() - 1)
                if self.is_red(self.original_image.get_at((x, y))):
                    green_shade = random.choice(green_shades)
                    self.leaves.append({
                        "position": (x, y),
                        "color": green_shade,
                        "type": "circle",
                        "radius": random.randint(1, 3),
                        "final_color": random.choice(self.yellow_shades),
                        "color_changed": False
                    })

        elif current_season == 'SUMMER':
            if len(self.leaves) >= self.MAX_GREEN_LEAVES:
                return
            else:           
                transformed_leaves = 0
                for leaf in self.leaves:
                    if leaf["type"] == "circle" and transformed_leaves < batch_size:
                        leaf["type"] = "ellipse"
                        leaf["width"] = random.randint(1, 3)
                        leaf["height"] = random.randint(6, 12)
                        leaf["angle"] = random.randint(0, 360)
                        transformed_leaves += 1
                
                additional_leaves_needed = leaves_to_add - transformed_leaves
                for _ in range(additional_leaves_needed):
                    x = random.randint(0, self.original_image.get_width() - 1)
                    y = random.randint(0, self.original_image.get_height() - 1)
                    if self.is_red(self.original_image.get_at((x, y))):
                        green_shade = random.choice(green_shades)
                        leaf_width = random.randint(1, 3)
                        leaf_height = random.randint(6, 12)
                        angle = random.randint(0, 360)
                        self.leaves.append({
                            "position": (x, y),
                            "color": green_shade,
                            "type": "ellipse",
                            "radius": random.randint(1, 3), 
                            "width": leaf_width,
                            "height": leaf_height,
                            "angle": angle,
                            "final_color": random.choice(self.yellow_shades),
                            "color_changed": False
                        })
                        
        elif current_season == "AUTUMN":
            if progress < 0.2:
                self.leaves_turning_into_yellow = True
        self.last_green_update = current_time

    def change_leaves_color_fade(self, target_color, current_time):
        leaves_already_target_color = sum(1 for leaf in self.leaves if leaf["color"] == target_color)
        
        if leaves_already_target_color >= len(self.leaves) / 2:
            leaf_color_change_batch_size = len(self.leaves) // 3
        else:
            leaf_color_change_batch_size = len(self.leaves) // 10

        leaves_to_change = random.sample(self.leaves, min(leaf_color_change_batch_size, len(self.leaves)))
        for leaf in leaves_to_change:
            leaf["color"] = target_color

    def check_all_leaves_color(self, target_color):
        return all(leaf["color"] == target_color for leaf in self.leaves)
    
    def remove_leaves(self, progress, season):
        if season == "AUTUMN" and progress > 0.8:
            fade_factor = (progress - 0.8) * 0.1
        elif season == "WINTER" and self.leaves:
            fade_factor = min(2, 8.0 / (len(self.leaves) + 1))
        else:
            return

        to_remove_leaves = [leaf for leaf in self.leaves if random.random() < fade_factor]
        for leaf in to_remove_leaves:
            self.leaves.remove(leaf)
    
    def update_leaf_colors_for_fall(self):
        current_time = self.game_state.get_current_time()
        if current_time - self.last_color_update_time < 1:
            return

        self.leaf_color_transition_progress += 1.0 / self.season_change_interval
        self.leaf_color_transition_progress = min(1, self.leaf_color_transition_progress)

        for leaf in self.leaves:
            if not leaf["color_changed"]:
                new_color = self.calculate_transition_color(leaf["color"], leaf["final_color"], self.leaf_color_transition_progress)
                leaf["color"] = new_color
                if leaf["color"] == leaf["final_color"]:
                    leaf["color_changed"] = True

        self.last_color_update_time = current_time

    def calculate_transition_color(self, start_color, end_color, progress):
        new_r = start_color[0] + (end_color[0] - start_color[0]) * progress
        new_g = start_color[1] + (end_color[1] - start_color[1]) * progress
        new_b = start_color[2] + (end_color[2] - start_color[2]) * progress
        return int(new_r), int(new_g), int(new_b)
    
    def get_snow_positions(self):
        positions = []
        for y in range(self.snow_image.get_height()):
            for x in range(self.snow_image.get_width()):
                if self.snow_image.get_at((x, y))[3] > 0:
                    positions.append((x, y))
        return positions
    
    '''
    #debug:
    def print_leaf_counts(self):
        circle_count = sum(1 for leaf in self.leaves if leaf["type"] == "circle")
        ellipse_count = sum(1 for leaf in self.leaves if leaf["type"] == "ellipse")

        print(f"Circle leaves: {circle_count}")
        #print(f"Ellipse leaves: {ellipse_count}")
    '''

