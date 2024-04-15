import numpy as np
import pygame
import pytest
from track import Track

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()

@pytest.fixture
def track():
    return Track('pics/track.png', 800, 600)

def test_grid_to_pixel_conversion(track):
    grid_pos = (0, 0)
    track_width = 800
    track_height = 600
    grid_rows = 100
    grid_columns = 100

    cell_width = track_width / grid_columns
    cell_height = track_height / grid_rows
    expected_pixel_x = (0.5) * cell_width
    expected_pixel_y = (0.5) * cell_height
    expected_pixel_pos = (int(expected_pixel_x), int(expected_pixel_y))

    assert track.grid_to_pixel_position(grid_pos) == expected_pixel_pos, f"Expected {expected_pixel_pos}, but got {track.grid_to_pixel_position(grid_pos)}"

def test_pixel_to_grid_conversion(track):
    pixel_pos = (0, 0)
    expected_grid_pos = (0, 0)
    assert track.pixel_to_grid_position(pixel_pos) == expected_grid_pos
    
def test_is_position_on_track(track):
    inside_position = (track.rect.centerx, track.rect.centery)
    outside_position = (track.rect.right + 10, track.rect.bottom + 10)

    assert track.is_position_on_track(*inside_position), "Position inside the track should be recognized as such."
    assert not track.is_position_on_track(*outside_position), "Position outside the track should not be recognized as on the track."
    
def test_heuristic(track):
    point_a1 = (0, 0)
    point_b1 = (1, 0)
    expected_distance1 = 1
    
    point_b2 = (1, 1)
    expected_distance2 = np.sqrt(2)

    calculated_distance1 = track.heuristic(point_a1, point_b1)
    
    calculated_distance2 = track.heuristic(point_a1, point_b2)

    assert calculated_distance1 == pytest.approx(expected_distance1), f"Expected distance {expected_distance1}, but got {calculated_distance1}"
    assert calculated_distance2 == pytest.approx(expected_distance2), f"Expected distance {expected_distance2}, but got {calculated_distance2}"
    
def test_get_neighbors(track):
    track.grid = np.array([
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1]
    ])
    
    test_node = (1, 0)
    expected_neighbors = [(0, 0), (0, 1), (2, 1)]
    
    actual_neighbors = track.get_neighbors(test_node)
    
    expected_neighbors.sort()
    actual_neighbors.sort()
    
    assert actual_neighbors == expected_neighbors, f"Expected neighbors {expected_neighbors}, but got {actual_neighbors}"
    
def test_astar_path_exists(track):
    track.grid = np.array([
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1]
    ])
    start = (0, 0)
    goal = (2, 2)

    expected_path = [(0, 1), (1, 2), (2, 2)]

    actual_path = track.astar(track.grid, start, goal)

    actual_path = actual_path[::-1]

    assert actual_path == expected_path, f"Expected path {expected_path}, but got {actual_path}"

def test_astar_no_path_exists(track):
    track.grid = np.array([
        [1, 0, 1],
        [1, 0, 1],
        [1, 0, 1]
    ])
    start = (0, 0)
    goal = (0, 2)

    assert track.astar(track.grid, start, goal) == False, "Expected no path to be found, but astar returned a path"
    
def test_get_traversable_positions(track):
    track.grid = np.array([
        [1, 0, 1],
        [0, 1, 0],
        [1, 1, 1]
    ])
    
    expected_traversable_positions = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 1), (2, 2)]
    
    actual_traversable_positions = track.get_traversable_positions()
    
    expected_traversable_positions.sort()
    actual_traversable_positions.sort()

    assert actual_traversable_positions == expected_traversable_positions, f"Expected traversable positions {expected_traversable_positions}, but got {actual_traversable_positions}"

