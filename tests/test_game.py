import pytest

from GameOfLife.game import Game

def test_incorrect_grid_size():
    with pytest.raises(ValueError):
        game = Game(0, 1)
    with pytest.raises(ValueError):
        game = Game(1, 0)
    with pytest.raises(ValueError):
        game = Game(-1, 1)
    with pytest.raises(ValueError):
        game = Game(1, -1)
