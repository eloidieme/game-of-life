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
    game = Game(100, 100, random_grid=False)
    assert np.all(game._initialize_grid() == 0)

def test_initialize_random_grid():
    game = Game(100, 100)
    assert np.any(game._initialize_grid() == 1)

def test_initialize_random_grid_with_proba():
    for proba in np.arange(0.1, 1.0, 0.2):
        game = Game(1000, 1000, alive_probability=proba)
        p = np.sum(game._initialize_grid() == 1) / (np.sum(game._initialize_grid() == 1) + np.sum(game._initialize_grid() == 0))
        assert np.abs(p - proba) < 0.1