import heapq
import json
import numpy as np
import pygame
from scipy.spatial import distance_matrix

class Track(pygame.sprite.Sprite):
    def __init__(self, image_path, screen_width, screen_height):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.grid = self.load_grid_from_file('grid/grid.json')
        self.calculate_heuristic_matrix()

    def load_grid_from_file(self, file_path):
        with open(file_path, 'r') as file:
            grid = json.load(file)
        return np.array(grid)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def is_position_on_track(self, x, y):
        relative_x = x - self.rect.left
        relative_y = y - self.rect.top
        if 0 <= relative_x < self.mask.get_size()[0] and 0 <= relative_y < self.mask.get_size()[1]:
            return self.mask.get_at((relative_x, relative_y))
        return False
    
    def calculate_heuristic_matrix(self):
        grid_points = np.indices(self.grid.shape).reshape(2, -1).T
        self.heuristic_matrix = distance_matrix(grid_points, grid_points)

    def heuristic(self, a, b):
        a_index = np.ravel_multi_index(a, self.grid.shape)
        b_index = np.ravel_multi_index(b, self.grid.shape)
        return self.heuristic_matrix[a_index, b_index]

    def get_neighbors(self, node):
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        neighbors = []
        for i, j in directions:
            neighbor = node[0] + i, node[1] + j
            if 0 <= neighbor[0] < self.grid.shape[0] and 0 <= neighbor[1] < self.grid.shape[1]:
                if self.grid[neighbor[0]][neighbor[1]] == 1:
                    neighbors.append(neighbor)
        return neighbors

    def astar(self, array, start, goal):
        neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        close_set = set()
        came_from = {}
        gscore = {start:0}
        fscore = {start:self.heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[start], start))
        
        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data
            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                if 0 <= neighbor[0] < array.shape[0] and 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 0:
                        continue
                else:
                    continue
                tentative_g_score = gscore[current] + self.heuristic(current, neighbor)
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue
                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return False
 
    
    def grid_to_pixel_position(self, grid_pos):
        cell_width = self.rect.width / self.grid.shape[1]
        cell_height = self.rect.height / self.grid.shape[0]
        pixel_x = (grid_pos[1] + 0.5) * cell_width + self.rect.left
        pixel_y = (grid_pos[0] + 0.5) * cell_height + self.rect.top
        return int(pixel_x), int(pixel_y)

    def pixel_to_grid_position(self, pixel_pos):
        cell_width = self.rect.width / self.grid.shape[1]
        cell_height = self.rect.height / self.grid.shape[0]
        grid_x = int((pixel_pos[0] - self.rect.left) / cell_width)
        grid_y = int((pixel_pos[1] - self.rect.top) / cell_height)
        grid_x = max(0, min(grid_x, self.grid.shape[1] - 1))
        grid_y = max(0, min(grid_y, self.grid.shape[0] - 1))
        return grid_y, grid_x
    
    def get_traversable_positions(self):
        traversable_positions = []
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                if self.grid[y][x] == 1:
                    traversable_positions.append((y, x))
        return traversable_positions
    
    def get_target_positions_from_image(image_path):
        image = pygame.image.load(image_path).convert_alpha()
        target_positions = []
        width, height = image.get_size()
        for y in range(height):
            for x in range(width):
                color = image.get_at((x, y))
                if color[3] > 0:
                    target_positions.append((x, y))
        return target_positions