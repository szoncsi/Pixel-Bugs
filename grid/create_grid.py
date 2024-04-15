import pygame
import json
import numpy as np

class TrackToGrid:
    def __init__(self, image_path, grid_dimension):
        pygame.init()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.grid_dimension = grid_dimension

    def is_position_on_track(self, x, y):
        if 0 <= x < self.rect.width and 0 <= y < self.rect.height:
            return self.mask.get_at((x, y)) > 0
        return False

    def create_grid(self):
        track_width, track_height = self.rect.size
        grid_rows, grid_cols = self.grid_dimension, self.grid_dimension
        cell_width = track_width / grid_cols
        cell_height = track_height / grid_rows

        grid = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]

        for row in range(grid_rows):
            for col in range(grid_cols):
                cell_x = int(col * cell_width + cell_width // 2)
                cell_y = int(row * cell_height + cell_height // 2)
                if self.is_position_on_track(cell_x, cell_y):
                    grid[row][col] = 1
        return grid

    def save_grid_to_file(self, grid, json_file_path, txt_file_path):
        with open(json_file_path, 'w') as file:
            json.dump(grid, file, indent=4)

        with open(txt_file_path, 'w') as file:
            for row in grid:
                file.write(''.join(str(cell) for cell in row) + '\n')

    def run(self, grid_file_path='grid/grid.json', txt_file_path='grid/grid.txt'):
        grid = self.create_grid()
        self.save_grid_to_file(grid, grid_file_path, txt_file_path)
        print(f"Grid saved to {grid_file_path} and {txt_file_path}")
        
        
    def load_grid_from_txt(self, txt_file_path):
        grid = []
        with open(txt_file_path, 'r') as file:
            for line in file:
                grid.append([int(cell) for cell in line.strip()])
        return grid

    def convert_txt_to_json(self, txt_file_path, json_file_path):
        grid = self.load_grid_from_txt(txt_file_path)
        with open(json_file_path, 'w') as file:
            json.dump(grid, file, indent=4)
        print(f"Converted TXT grid to JSON: {json_file_path}")

if __name__ == "__main__":
    image_path = 'pics/track.png'
    grid_dimension = 100
    track_to_grid = TrackToGrid(image_path, grid_dimension)
    track_to_grid.convert_txt_to_json('grid/grid_edited.txt', 'grid/grid_from_txt.json')