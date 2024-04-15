import math
import random
import numpy as np
import pygame
from pixels.pheromone_trail import PheromoneTrail
from states.bug_state import BugState
from pixels.pixel import Pixel
from track import Track

class Bug(Pixel):
    def __init__(self, color, width, height, screen_width, screen_height, game_state, block_size, parents=None, **kwargs):
        super().__init__(color, width, height)
    
        self.gender = kwargs.get('gender', random.choice(["male", "female"]))
        self.energy = kwargs.get('energy', 100)
        self.lifespan = kwargs.get('lifespan', 8)
        self.hasMated = kwargs.get('hasMated', False)
        self.is_active = kwargs.get('is_active', True)
        self.generation = kwargs.get('generation', 1)
        self.isGravid = kwargs.get('isGravid', False if self.gender == "female" else None)
        self.mate = kwargs.get('mate', None)
        self.searching_for_mate = kwargs.get('searching_for_mate', False)

        if parents:
            self.genotype = self.inherit_genes(parents)
        else:
            self.genotype = {
                'speed': random.choice(['AA', 'Aa', 'aA', 'aa']),
                'toughness': random.choice(['BB', 'Bb', 'bB', 'bb']),
                'sensing_distance': random.choice(['CC', 'Cc', 'cC', 'cc']),
                'color': random.choice(['DD', 'Dd', 'dD', 'dd']),
                'pigment': random.choice(['ee', 'Ee', 'eE', 'EE'])
            }
        
        self.calculate_phenotype()           
        self.max_movement_speed = self.movement_speed 
        self.game_state = game_state
        self.last_energy_update_time = self.game_state.get_current_time()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_size = block_size * 1
        self.angle = 0
        self.rotation_speed = 1.5
        self.state = BugState.SEARCHING
        self.target = None
        random_direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        random_direction.normalize_ip()
        self.movement_vector = random_direction
        self.previous_x = 0
        self.previous_y = 0
        self.attempts_to_move = 0
        self.target_angle = self.angle
        self.target_path = []
        self.freeze_until = None
        self.grid_pos = self.game_state.track.pixel_to_grid_position((self.rect.x, self.rect.y))
        self.winter_hide_positions = Track.get_target_positions_from_image('pics/bark.png')
        self.hide_position = None
        self.step_counter = 0
        self.sensed_pheromones = [] 
        self.bug_structure = [
                                (2, 0),               (8, 0),
                                   (3, 1),        (7, 1),
                                       (4, 2),(6, 2),
                  (1, 3),                 (5, 3),               (9, 3),
                       (2, 4),    (4, 4), (5, 4), (6, 4),    (8, 4),
                          (3, 5), (4, 5), (5, 5), (6, 5),(7, 5),
                          (3, 6), (4, 6), (5, 6), (6, 6),(7, 6),
                   (2, 7),(3, 7), (4, 7), (5, 7), (6, 7),(7, 7),(8, 7),
            (1, 8),(2, 8),(3, 8), (4, 8), (5, 8), (6, 8),(7, 8),(8, 8),(9, 8),
        (0, 9),    (2, 9),(3, 9), (4, 9), (5, 9), (6, 9),(7, 9),(8, 9),    (10, 9),
                        (3, 10), (4, 10), (5, 10), (6, 10),(7, 10),
                        (3, 11), (4, 11), (5, 11), (6, 11),(7, 11),
                     (2, 12),    (4, 12), (5, 12), (6, 12),    (8, 12),
                 (1, 13),                 (5, 13),                 (9, 13)
        ]

        self.calculate_dimensions()
        self.create_surface()
        self.original_image = self.image
    
    def inherit_genes(self, parents):
        child_genotype = {}
        for trait in ['speed', 'toughness', 'sensing_distance', 'pigment']:
            child_genotype[trait] = random.choice(parents['mom'][trait]) + random.choice(parents['dad'][trait])

        mom_color = random.choice(parents['mom']['color'])
        dad_color = random.choice(parents['dad']['color'])

        mutated_color = self.mutate_gene(mom_color + dad_color)

        child_genotype['color'] = mutated_color

        return child_genotype

    def calculate_phenotype(self):
        if 'ee' in self.genotype['pigment']:
            self.color = (255, 228, 196)
        else:
            if 'D' in self.genotype['color']:
                self.color = (75, 37, 0)
            elif 'r' in self.genotype['color']:
                self.color = (128, 0, 0),
            elif 'dd' in self.genotype['color']:
                self.color = (150, 75, 0)
        
        self.movement_speed = self.calculate_trait_phenotype('speed', base=1.0, dominant_effect=0.5, recessive_effect=-0.25)

        self.toughness = self.calculate_trait_phenotype('toughness', base=50, dominant_effect=25, recessive_effect=-15)

        self.sensing_distance = self.calculate_trait_phenotype('sensing_distance', base=10, dominant_effect=5, recessive_effect=-3)

    def calculate_trait_phenotype(self, trait, base, dominant_effect, recessive_effect):
        genes = self.genotype[trait]
        trait_value = base

        if 'A' in genes or 'B' in genes or 'C' in genes:
            trait_value += dominant_effect
        if genes.count('a') == 2 or genes.count('b') == 2 or genes.count('c') == 2:
            trait_value += recessive_effect

        return trait_value

    def mutate_gene(self, color_genotype):
        mutation_rate = 0.1
        mutated_color = color_genotype

        if random.random() < mutation_rate:
            if 'r' not in color_genotype:
                mutated_color = 'r' + random.choice(['D', 'd'])

        return mutated_color
        
    def calculate_dimensions(self):
        self.min_x = min(pos[0] for pos in self.bug_structure)
        self.max_x = max(pos[0] for pos in self.bug_structure)
        self.min_y = min(pos[1] for pos in self.bug_structure)
        self.max_y = max(pos[1] for pos in self.bug_structure)
        self.width = (self.max_x - self.min_x + 1) * self.block_size
        self.height = (self.max_y - self.min_y + 1) * self.block_size
    
    def create_surface(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for pos in self.bug_structure:
            block_rect = pygame.Rect(
                (pos[0] - self.min_x) * self.block_size,
                (pos[1] - self.min_y) * self.block_size,
                self.block_size, self.block_size)
            pygame.draw.rect(self.image, self.color, block_rect)
        self.rect = self.image.get_rect(center=(self.screen_width / 2, self.screen_height / 2))

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.image, self.rect.topleft)

            # Állapot megjelenítése (BugState)
            #font = pygame.font.SysFont(None, 15)
            #state_text = font.render(str(self.state), True, (255, 255, 255))
            #screen.blit(state_text, (self.rect.x, self.rect.y - 20))
                
    def rotate_to_movement_direction(self):
        if self.movement_vector.length() > 0:
            angle = math.degrees(math.atan2(-self.movement_vector.y, self.movement_vector.x)) - 90
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)
                
    def update_movement_vector(self):
        if self.target:
            target_vector = pygame.math.Vector2(self.target) - pygame.math.Vector2(self.rect.center)
            if target_vector.length() > 0:
                target_vector.normalize_ip()

            wander_strength = 0.2
            wander_vector = pygame.math.Vector2(random.uniform(-wander_strength, wander_strength), random.uniform(-wander_strength, wander_strength))
            
            self.movement_vector = (self.movement_vector * 0.5 + target_vector * 0.5 + wander_vector).normalize()
    
    def update(self):
        self.update_energy()
        self.adjust_movement_speed_based_on_energy()
        self.update_behavior()
        self.update_movement_vector()
        self.rotate_to_movement_direction()

    def update_position(self):
        if not self.is_position_walkable(self.rect.centerx, self.rect.centery):
            new_pos = self.find_nearest_walkable_position((self.rect.centerx, self.rect.centery))
            if new_pos:
                self.rect.centerx, self.rect.centery = new_pos
                self.update_movement_vector()
                self.rotate_to_movement_direction()
                new_target = self.select_nearby_random_point(max_distance=5)
                if new_target:
                    self.target_path = self.calculate_path_to_target(new_target)
    
    def update_energy(self):
        current_time = self.game_state.get_current_time()
        
        energy_decrement = 1

        if self.game_state.current_season.name == 'WINTER':
            if self.is_active:
                energy_decrement *= 4
            else:
                energy_decrement *= 0.75

        energy_decrement *= (1 - self.toughness / 250)
        energy_decrement *= (1 + self.movement_speed / 5)

        if current_time - self.last_energy_update_time >= 1:
            self.energy -= max(energy_decrement, 0.2)
            self.last_energy_update_time = current_time

            if self.energy <= 0:
                self.kill()
    
    def adjust_movement_speed_based_on_energy(self):
        base_speed = self.max_movement_speed
        min_speed = 2
        energy_ratio = self.energy / 100.0
        self.movement_speed = min_speed + (base_speed - min_speed) * energy_ratio
    
    def update_behavior(self):
        if not self.is_active:
            self.spring_awakening()
            return
        
        if self.game_state.current_season.name == 'WINTER':
            self.update_position()
            self.winter_hide()
            if self.target_path:
                self.move_on_path()
            else:
                nearby_point = self.select_nearby_random_point(max_distance=5)
                if nearby_point:
                    self.state = BugState.FOLLOWING
                    self.target_path = [self.game_state.track.pixel_to_grid_position(nearby_point)]
            self.avoid_collisions_with_other_bugs()
            return

        self.update_position()
            
        if self.target_path:
            self.move_on_path()          
        else:
            self.search_for_food_or_point()
            
        if self.game_state.current_season.name == 'SUMMER' and self.energy > 50:
            if (self.gender == 'female' and self.isGravid == False) or self.gender == 'male':
                self.clean_sensed_pheromones()
                self.seek_mate()
                self.handle_mating_collision()          
        else:
            self.searching_for_mate = False
        if self.game_state.current_season.name == 'AUTUMN' and self.hasMated:
            self.searching_for_mate = False
            self.mate = None
                
        self.handle_food_collision()
            
        self.avoid_collisions_with_other_bugs()
        
    def winter_hide(self):
        if not self.hide_position:
            self.hide_position = self.select_winter_hide_position()
            if self.hide_position:
                self.target_path = self.calculate_path_to_target(self.hide_position)
           
        if self.hide_position and self.reached_target(self.hide_position):
            self.is_active = False
            self.target_path = []
    
    def spring_awakening(self):
        if self.game_state.current_season.name == 'SPRING':
            self.is_active = True
            if self.gender == 'female':
                self.isGravid = False
                self.hasMated = False

    def handle_food_collision(self):
        collided_sap = pygame.sprite.spritecollideany(self, self.game_state.tree_sap_list)
        if collided_sap:
            self.state = BugState.EATING
            self.energy = min(100, self.energy + 10)
            collided_sap.kill()

    def search_for_food_or_point(self):
        self.state = BugState.SEARCHING    
        food_detected, food_location = self.detect_food()
        if food_detected:
            self.target_path = self.calculate_path_to_target(food_location)
        else:  
            #sap_disappeared = self.target and not any(sap.rect.center == self.target for sap in self.game_state.tree_sap_list)
            nearby_point = self.select_nearby_random_point(max_distance=30)
            if nearby_point:
                self.state = BugState.FOLLOWING
                self.target_path = [self.game_state.track.pixel_to_grid_position(nearby_point)]
    
    def calculate_path_to_target(self, target):
            start_pos = self.game_state.track.pixel_to_grid_position(self.rect.center)
            target_pos = self.game_state.track.pixel_to_grid_position(target)

            if self.game_state.track.grid[start_pos[0], start_pos[1]] != 1 or self.game_state.track.grid[target_pos[0], target_pos[1]] != 1:
                return [start_pos]

            path = self.game_state.track.astar(self.game_state.track.grid, start_pos, target_pos)
            
            if path:
                return path
            else:
                return [start_pos]

    def detect_food(self):
        closest_food = None
        min_distance = float('inf')
        for food in self.game_state.tree_sap_list:
            bug_position = pygame.math.Vector2(self.rect.center)
            food_position = pygame.math.Vector2(food.rect.center)
            
            distance = bug_position.distance_to(food_position)
            if distance < self.sensing_distance and distance < min_distance:
                closest_food = food
                min_distance = distance

        if closest_food:
            return True, closest_food.rect.center
        else:
            return False, None
        
    def select_nearby_random_point(self, max_distance=30):
        traversable_positions = self.game_state.track.get_traversable_positions()
        possible_targets = []
        current_grid_pos = self.game_state.track.pixel_to_grid_position((self.rect.x, self.rect.y))
        
        for pos in traversable_positions:
            
            if abs(pos[0] - current_grid_pos[0]) <= max_distance and abs(pos[1] - current_grid_pos[1]) <= max_distance:
                possible_targets.append(pos)
                
        if possible_targets:
            selected_grid_pos = random.choice(possible_targets)
            return self.game_state.track.grid_to_pixel_position(selected_grid_pos)
        else:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
            
            for dx, dy in directions:
                neighbor_pos = (current_grid_pos[0] + dy, current_grid_pos[1] + dx)
                
                if 0 <= neighbor_pos[0] < self.game_state.track.grid.shape[0] and 0 <= neighbor_pos[1] < self.game_state.track.grid.shape[1]:
                    
                    if self.game_state.track.grid[neighbor_pos] == 1:
                        return self.game_state.track.grid_to_pixel_position(neighbor_pos)
            return self.game_state.track.grid_to_pixel_position(current_grid_pos)
    
    def move_on_path(self):   
        if self.target_path:
            self.target = self.game_state.track.grid_to_pixel_position(self.target_path[0])
            self.move_towards(self.target)
            
            if self.close_to(self.target):
                self.target_path.pop(0)

                if self.target_path:
                    self.target = self.game_state.track.grid_to_pixel_position(self.target_path[0])
                else:
                    self.target = None
            
    def reached_target(self, target):
        if not target:
            return False
        target_vector = pygame.math.Vector2(target) - pygame.math.Vector2(self.rect.center)
        return target_vector.length() <= 10
                
    def move_towards(self, target_pixel):
        direction_vector = pygame.math.Vector2(target_pixel) - pygame.math.Vector2(self.rect.center)
        if direction_vector.length() > 0:
            direction_vector.normalize_ip()
        self.rect.x += direction_vector.x * self.movement_speed
        self.rect.y += direction_vector.y * self.movement_speed
        self.update_movement_vector()
        self.rotate_to_movement_direction()
        
    def close_to(self, target_pixel, threshold=10):
        distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(target_pixel))
        return distance <= threshold              
    
    def update_bugs_grid_positions(self):
        for bug in self.game_state.bug_list:
            grid_pos = self.game_state.track.pixel_to_grid_position((bug.rect.x, bug.rect.y))
            bug.grid_pos = grid_pos
    
    def is_position_walkable(self, x, y):
        grid_pos = self.game_state.track.pixel_to_grid_position((x, y))
        if 0 <= grid_pos[0] < self.game_state.track.grid.shape[0] and 0 <= grid_pos[1] < self.game_state.track.grid.shape[1]:
            return self.game_state.track.grid[grid_pos[0], grid_pos[1]] == 1
        else:
            return False  
     
    def find_nearest_walkable_position(self, start_pos):
        traversable_positions = self.game_state.track.get_traversable_positions()
        start_grid_pos = self.game_state.track.pixel_to_grid_position(start_pos)
        nearest_pos = None
        min_distance = float('inf')
        for pos in traversable_positions:
            distance = self.game_state.track.heuristic(start_grid_pos, pos)
            if distance < min_distance:
                min_distance = distance
                nearest_pos = pos
        
        if nearest_pos is not None:
            return self.game_state.track.grid_to_pixel_position(nearest_pos)
        return None  
    
    def avoid_collisions_with_other_bugs(self):
        self.state = BugState.AVOIDING
        collided_bug = pygame.sprite.spritecollideany(self, self.game_state.bug_list)
        if collided_bug and collided_bug != self:
            avoidance_vector = pygame.math.Vector2(self.rect.centerx - collided_bug.rect.centerx, self.rect.centery - collided_bug.rect.centery)
            if avoidance_vector.length() > 0:
                avoidance_vector.normalize_ip()
            else:
                avoidance_vector = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

            self.movement_vector = (self.movement_vector + avoidance_vector * 0.5).normalize()

            self.rect.x += self.movement_vector.x * self.movement_speed * 0.5
            self.rect.y += self.movement_vector.y * self.movement_speed * 0.5

            self.rect.x = max(0, min(self.rect.x, self.screen_width - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, self.screen_height - self.rect.height))

            self.update_movement_vector()
            self.rotate_to_movement_direction()
            
    def seek_mate(self):
        self.state = BugState.SEARCHING_FOR_MATE
        progress = self.game_state.get_progress()
        mating_prob = min(0.5, progress * 0.5)
            
        if random.random() < mating_prob or self.searching_for_mate == True: 
            self.searching_for_mate = True
            
            if self.gender == 'male':
                self.follow_pheromones()
            else:
                self.leave_pheromone_trail()
                
    def leave_pheromone_trail(self):
        self.step_counter += 1
        if self.game_state.current_season.name in ['SPRING', 'SUMMER'] and self.step_counter % 10 == 0:
            pheromone_trail = PheromoneTrail(self.rect.center)
            self.game_state.pheromone_trails.add(pheromone_trail)
        if self.step_counter >= 10:
            self.step_counter = 0
                
    def find_mate(self):
        MAX_SEARCH_DISTANCE = 40
        
        if not self.mate:
            closest_mate = None
            closest_distance = float('inf')

            for bug in self.game_state.bug_list:
                
                if bug != self and bug.gender != self.gender and bug.searching_for_mate == True:
                    
                    if self.gender == 'female' and self.isGravid == False:
                        distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(bug.rect.center))
                        
                        if distance < MAX_SEARCH_DISTANCE and distance < closest_distance:
                            closest_distance = distance
                            closest_mate = bug
                    
                    elif self.gender == 'male' and bug.isGravid == False:
                        distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(bug.rect.center))
                        
                        if distance < MAX_SEARCH_DISTANCE and distance < closest_distance:
                            closest_distance = distance
                            closest_mate = bug

            if closest_mate is not None:
                self.mate = closest_mate

        elif self.mate.searching_for_mate == True:
            self.target_path = self.calculate_path_to_target(self.mate.rect.center)         

    def follow_pheromones(self):
        MAX_SEARCH_DISTANCE = 40
        SEARCH_DISTANCE = 5
        closest_trail = None
        closest_distance = float('inf')
        max_lifespan = -1

        for trail in self.game_state.pheromone_trails:
            if trail in self.sensed_pheromones:
                continue

            distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(trail.rect.center))
            if distance < closest_distance and distance > SEARCH_DISTANCE and trail.lifespan > max_lifespan:
                max_lifespan = trail.lifespan
                closest_distance = distance
                closest_trail = trail

        if closest_trail is not None:
            if MAX_SEARCH_DISTANCE > closest_distance > SEARCH_DISTANCE:
                self.target_path = self.calculate_path_to_target(closest_trail.rect.center)
                self.sensed_pheromones.append(closest_trail)
            elif closest_distance <= SEARCH_DISTANCE:
                self.target = closest_trail.rect.center
                self.move_towards(self.target)
                self.sensed_pheromones.append(closest_trail)
        self.find_female()
                
    def find_female(self):
        MAX_DISTANCE = 3
        closest_mate = None
        closest_distance = float('inf')

        for bug in self.game_state.bug_list:
            if self.gender == 'male' and bug.gender != self.gender and bug.searching_for_mate == True and bug.isGravid == False:
                distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(bug.rect.center))
                if distance < MAX_DISTANCE and distance < closest_distance:
                    closest_distance = distance
                    closest_mate = bug
        if closest_mate is not None and closest_mate.searching_for_mate == True:
            self.target_path = self.calculate_path_to_target(closest_mate.rect.center)
                
    def handle_mating_collision(self):
        if self.searching_for_mate:
            collided_bugs = pygame.sprite.spritecollide(self, self.game_state.bug_list, False)
            for bug in collided_bugs:
                if bug != self and bug.gender != self.gender and bug.searching_for_mate:
                    self.mate = bug
                    self.mating()
                    break
            self.avoid_collisions_with_other_bugs()
                
    def mating(self):
        if self.mate is not None:
            if self.gender == "female" and not self.isGravid and self.mate is not None:
                self.isGravid = True
                num_offspring = random.randint(2, 5)
                for _ in range(num_offspring):
                    pupa_attributes = self.generate_pupa_attributes()
                    self.game_state.pupa_list.append(pupa_attributes)
                print(f"{self} and {self.mate} have mated and produced {num_offspring} offspring.")
            if self.mate and self.mate.gender == "female" and not self.mate.isGravid:
                self.mate.isGravid = True
                num_offspring = random.randint(2, 5)
                for _ in range(num_offspring):
                    pupa_attributes = self.mate.generate_pupa_attributes()
                    self.game_state.pupa_list.append(pupa_attributes)
                print(f"{self} and {self.mate} have mated and produced {num_offspring} offspring.")
                
        self.hasMated = True
        self.mate.hasMated = True
        self.searching_for_mate = False
        self.target = None
        self.mate = None

    def generate_pupa_attributes(self):
        if self.mate is not None:
            new_genotype = {
                'color': self.combine_genes(self.genotype['color'], self.mate.genotype['color']),
                'speed': self.combine_genes(self.genotype['speed'], self.mate.genotype['speed']),
                'toughness': self.combine_genes(self.genotype['toughness'], self.mate.genotype['toughness']),
                'sensing_distance': self.combine_genes(self.genotype['sensing_distance'], self.mate.genotype['sensing_distance'])
            }
            
            color_phenotype = self.determine_color(new_genotype['color'])
            speed_phenotype = self.calculate_trait_phenotype('speed', base=1.0, dominant_effect=0.5, recessive_effect=-0.25)
            toughness_phenotype = self.calculate_trait_phenotype('toughness', base=50, dominant_effect=25, recessive_effect=-15)
            sensing_distance_phenotype = self.calculate_trait_phenotype('sensing_distance', base=10, dominant_effect=5, recessive_effect=-3)

            pupa_attributes = {
                'color': color_phenotype,
                'movement_speed': speed_phenotype,
                'toughness': toughness_phenotype,
                'sensing_distance': sensing_distance_phenotype,
                'generation': max(self.generation, self.mate.generation) + 1,
            }

            return pupa_attributes

    def combine_genes(self, gene1, gene2):
        new_gene = random.choice(gene1) + random.choice(gene2)
        return new_gene

    def determine_color(self, genotype):
        if 'D' in genotype:
            return (75, 37, 0)
        elif 'r' in genotype:
            return (128, 0, 0)
        else:
            return (205, 133, 63)
        
    def clean_sensed_pheromones(self):
        active_pheromones = [pheromone for pheromone in self.sensed_pheromones if pheromone in self.game_state.pheromone_trails]
        self.sensed_pheromones = active_pheromones
    
    
    def select_winter_hide_position(self):
        if not self.winter_hide_positions:
            return None

        current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        closest_pos = None
        min_distance = float('inf')

        for pos in self.winter_hide_positions:
            target_pos = pygame.math.Vector2(pos)
            distance = current_pos.distance_to(target_pos)
            
            if distance < min_distance:
                min_distance = distance
                closest_pos = pos

        return closest_pos if closest_pos else None