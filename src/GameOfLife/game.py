from pathlib import Path
from typing import Optional

import numpy as np

from GameOfLife import logger


class Game:
    """
    Main game class that handles grid initialization, 
    I/O operations and game updates.

    Attributes
    ----------
    grid_size: (int, int)
        Dimensions of the grid.
        Can be infered from a grid file if both lengths are set to None.
    random_grid: bool
        Specifies if the grid should be randomly generated.
    starting_grid_filepath: str
        Path of the grid file if the grid should be imported.
    random_seed: int
        A seed used to have predictable results with random 
        grid generation.
    alive_probability: float
        The probability that an individual cell is created alive
        for random grid generation.
    
    Methods
    -------
    _parse_grid_from_file() -> grid
        Creates a grid from a .txt file input containing 0s and 1s.
    _save_grid_to_file(grid, path)
        Static method that saves a given grid to a .txt file.
    _initialize_grid() -> grid
        Creates a grid using the class attributes (dead, random or from file).
    update_grid_state(grid) -> grid
        Creates the next grid from a given grid using the rules of the game.
    """
    def __init__(
            self,
            grid_height: Optional[int] = None,
            grid_width: Optional[int] = None,
            random_grid: bool = True,
            starting_grid_filepath: Optional[str] = None,
            random_seed: Optional[int] = None,
            alive_probability: float = 0.5
    ) -> None:
        if grid_height and grid_width:
            self.grid_size = (grid_height, grid_width)
            if grid_height <= 0 or grid_width <= 0:
                logger.error(
                    "Grid width and height must be positive if specified.")
                raise ValueError
        else:
            self.grid_size = None

        if not grid_height and grid_width or not grid_width and grid_height:
            logger.error(
                "Grid width and height must be both specified if one of them is.")
            raise ValueError

        if not grid_height and not starting_grid_filepath:
            logger.error("Either grid size or file path must be specified.")
            raise ValueError

        self.starting_grid_filepath = starting_grid_filepath
        self.random_grid = random_grid
        if starting_grid_filepath:
            self.random_grid = False
        if random_seed:
            np.random.seed(random_seed)
        self.alive_probability = alive_probability

    def _parse_grid_from_file(self) -> np.ndarray:

        file_path = Path(self.starting_grid_filepath)
        grid = []
        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            row = []
            for char in line:
                if (char != '\n'):
                    if char not in ["0", "1"]:
                        logger.error(
                            "Incorrect value in import file. Values must be 0 or 1.")
                        raise ValueError
                    row.append(int(char))
            grid.append(row)
        grid = np.array(grid)

        return np.array(grid)

    @staticmethod
    def _save_grid_to_file(grid: np.ndarray, path: str) -> None:
        save_path = Path(path)
        try:
            np.savetxt(save_path, grid, fmt='%i', delimiter='')
            logger.info("Grid successfully saved.")
        except Exception as e:
            logger.error(f"Exception occured while saving: {e}")

    def _initialize_grid(self) -> np.ndarray:
        """
        Initializes a grid using the class attributes (random or file-loaded).
        Defaults to a dead grid (meaning all the cells are set to zero).
        """
        if self.grid_size:
            grid = np.zeros(self.grid_size)

        if self.starting_grid_filepath:
            grid = self._parse_grid_from_file()

        if self.random_grid:
            grid = np.random.choice([0, 1], self.grid_size, p=[
                                    1 - self.alive_probability, self.alive_probability])

        return grid

    def _update_grid_state(self, grid: np.ndarray) -> np.ndarray:
        (grid_height, grid_width) = grid.shape
        updated_grid = grid.copy()
        for i in range(grid_height):
            for j in range(grid_width):
                alive_neighbours_count = 0
                for k in range(i-1, i+2):
                    for l in range(j-1, j+2):
                        if (k, l) != (i, j) and grid[(k % grid_height, l % grid_width)]:
                            alive_neighbours_count += 1
                if not grid[i, j] and alive_neighbours_count == 3:
                    updated_grid[i, j] = 1
                if grid[i, j] and alive_neighbours_count not in [2, 3]:
                    updated_grid[i, j] = 0
        return updated_grid
