import os

import pytest
import numpy as np

from GameOfLife.game import Game

np.random.seed(42)


def test_incorrect_grid_size():
    """Verify that initializing the game with invalid grid sizes raises a ValueError."""
    sizes = [
        (0, 1),
        (1, 0),
        (-1, 1),
        (1, -1),
        (None, 1),
        (1, None),
    ]
    for (height, width) in sizes:
        with pytest.raises(ValueError):
            game = Game(height, width)


def test_no_size_and_no_path():
    """Ensure that the game raises a ValueError when initialized without a size and file path."""
    with pytest.raises(ValueError):
        game = Game()


def test_initialize_dead_grid():
    """Check that grids initialized without the random_grid flag are dead (all zeros)."""
    sizes = [(100, 100), (50, 20), (20, 50)]
    for (width, height) in sizes:
        game = Game(height, width, random_grid=False)
        grid = game.initialize_grid()
        assert np.all(grid == 0)
        assert grid.shape == (height, width)


def test_initialize_random_grid():
    """Test that grids initialized with the random_grid flag contain both alive and dead cells."""
    sizes = [(100, 100), (50, 20), (20, 50)]
    for (width, height) in sizes:
        game = Game(height, width)
        grid = game.initialize_grid()
        assert np.any(grid == 1)
        assert np.any(grid == 0)
        assert np.all((grid == 0) | (grid == 1))
        assert grid.shape == (height, width)


def test_initialize_random_grid_with_proba():
    """Check that the alive_probability parameter accurately influences the density of alive cells."""
    for proba in np.arange(0.1, 1.0, 0.2):
        game = Game(1000, 1000, alive_probability=proba)
        grid = game.initialize_grid()
        p = np.sum(grid == 1) / grid.size
        assert np.abs(p - proba) < 0.1


def test_import_from_file():
    """Ensure that grids imported from files match the expected configurations."""
    test_grids = [
        np.array([[0, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0]]),

        np.array([[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 1, 1, 1, 0],
                  [0, 0, 0, 0, 0]]),
    ]
    paths = [f"data/test_grid_{i}.txt" for i in range(2)]
    sizes = [(3, 3), (4, 5)]
    for i in range(2):
        game = Game(sizes[i][0], sizes[i][1], starting_grid_filepath=paths[i])
        grid = game._parse_grid_from_txt()
        assert np.all(grid == test_grids[i])


def test_import_from_file_incorrect_value():
    """Test that importing a grid from a file with incorrect values raises a ValueError."""
    test_path = 'data/test_grid_incorrect_value.txt'
    with pytest.raises(ValueError):
        game = Game(3, 3, starting_grid_filepath=test_path)
        game._parse_grid_from_txt()


def test_save_grid_to_file():
    """Verify that grids can be saved to a file and then imported with identical configuration."""
    grid = np.array(
        [[0, 0, 0],
         [0, 1, 0],
         [0, 0, 0]])
    save_path = 'data/test_save.txt'
    Game.save_grid_to_file(grid, save_path)
    assert os.path.isfile(save_path)

    game = Game(3, 3, starting_grid_filepath=save_path)
    imported_grid = game._parse_grid_from_txt()
    assert np.all(grid == imported_grid)
    os.remove(save_path)


def test_update_dead_grid():
    """Confirm that updating a dead grid results in no changes."""
    grid = np.array(
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]])
    (width, height) = grid.shape
    game = Game(height, width)
    assert np.all(grid == game.update_grid_state(grid))


def test_stay_alive():
    """Check that cells with two or three neighbors stay alive through the update."""
    initial_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ])
    expected_next_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0,]
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))


def test_overpopulation():
    """Verify that cells with more than three neighbors die from overpopulation."""
    initial_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ])
    expected_next_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))


def test_reproduction():
    """Ensure that dead cells with exactly three neighbors become alive."""
    initial_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    expected_next_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))


def test_oscillator():
    """Test that oscillators toggle between states correctly."""
    initial_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    expected_next_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))
    assert np.all(initial_grid == game.update_grid_state(expected_next_grid))


def test_neighbour_wrapping():
    """Verify that neighbor wrapping works as expected for edge cells."""
    initial_grid = np.array([
        [1, 0, 0],
        [0, 1, 1],
        [0, 0, 0],
    ])
    expected_next_grid = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))


def test_smaller_grids():
    """Ensure the game correctly handles smaller grids, including single-cell grids."""
    initial_grid = np.array([
        [0, 1],
        [0, 0]
    ])
    expected_next_grid = np.array([
        [0, 0],
        [0, 0]
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))

    initial_grid = np.array([
        [1]
    ])
    expected_next_grid = np.array([
        [0]
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game.update_grid_state(initial_grid))
