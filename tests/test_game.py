import os

import pytest
import numpy as np

from GameOfLife.game import Game

np.random.seed(42)


def test_incorrect_grid_size():
    with pytest.raises(ValueError):
        game = Game(0, 1)
    with pytest.raises(ValueError):
        game = Game(1, 0)
    with pytest.raises(ValueError):
        game = Game(-1, 1)
    with pytest.raises(ValueError):
        game = Game(1, -1)


def test_initialize_dead_grid():
    sizes = [(100, 100), (50, 20), (20, 50)]
    for (width, height) in sizes:
        game = Game(height, width, random_grid=False)
        grid = game._initialize_grid()
        assert np.all(grid == 0)
        assert grid.shape == (height, width)


def test_initialize_random_grid():
    sizes = [(100, 100), (50, 20), (20, 50)]
    for (width, height) in sizes:
        game = Game(height, width)
        grid = game._initialize_grid()
        assert np.any(grid == 1)
        assert np.any(grid == 0)
        assert np.all((grid == 0) | (grid == 1))
        assert grid.shape == (height, width)


def test_initialize_random_grid_with_proba():
    for proba in np.arange(0.1, 1.0, 0.2):
        game = Game(1000, 1000, alive_probability=proba)
        p = np.sum(game._initialize_grid() == 1) / \
            (np.sum(game._initialize_grid() == 1) +
             np.sum(game._initialize_grid() == 0))
        assert np.abs(p - proba) < 0.1


def test_import_from_file():
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
        grid = game._parse_grid_from_file()
        assert np.all(grid == test_grids[i])


def test_import_from_file_wrong_size():
    test_path = 'data/test_grid_0.txt'
    with pytest.raises(ValueError):
        game = Game(4, 4, starting_grid_filepath=test_path)
        game._parse_grid_from_file()


def test_import_from_file_incorrect_value():
    test_path = 'data/test_grid_incorrect_value.txt'
    with pytest.raises(ValueError):
        game = Game(3, 3, starting_grid_filepath=test_path)
        game._parse_grid_from_file()


def test_save_grid_to_file():
    grid = np.array(
        [[0, 0, 0],
         [0, 1, 0],
         [0, 0, 0]])
    save_path = 'data/test_save.txt'
    Game._save_grid_to_file(grid, save_path)
    assert os.path.isfile(save_path)

    game = Game(3, 3, starting_grid_filepath=save_path)
    imported_grid = game._parse_grid_from_file()
    assert np.all(grid == imported_grid)
    os.remove(save_path)


def test_update_dead_grid():
    grid = np.array(
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]])
    (width, height) = grid.shape
    game = Game(height, width)
    assert np.all(grid == game._update_grid_state(grid))


def test_stay_alive():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))


def test_overpopulation():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))


def test_reproduction():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))

def test_oscillator():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))
    assert np.all(initial_grid == game._update_grid_state(expected_next_grid))

def test_neighbour_wrapping():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))

def test_smaller_grids():
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
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))

    initial_grid = np.array([
        [1]
    ])
    expected_next_grid = np.array([
        [0]
    ])
    (width, height) = initial_grid.shape
    game = Game(height, width)
    assert np.all(expected_next_grid == game._update_grid_state(initial_grid))