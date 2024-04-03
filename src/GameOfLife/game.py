from pathlib import Path
from typing import Optional

import numpy as np

from GameOfLife import logger


class Game:
    def __init__(
            self,
            grid_width,
            grid_height,
            random_grid: bool = True,
            starting_grid_filepath: Optional[str] = None,
            random_seed: Optional[int] = None,
            alive_probability: float = 0.5
    ) -> None:
        if grid_height <= 0 or grid_width <= 0:
            logger.error("Grid width and height must be positive.")
            raise ValueError

        self.grid_size = (grid_width, grid_height)
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
                        logger.error("Incorrect value in import file. Values must be 0 or 1.")
                        raise ValueError
                    row.append(int(char))
            grid.append(row)
        grid = np.array(grid)

        if grid.shape != self.grid_size:
            logger.error("Size of imported grid and entered grid size do not match.")
            raise ValueError

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
        grid = np.zeros(self.grid_size, dtype=np.bool_)

        if self.starting_grid_filepath:
            grid = self._parse_grid_from_file()

        if self.random_grid:
            grid = np.random.choice([0, 1], self.grid_size, p=[
                                    1 - self.alive_probability, self.alive_probability])

        return grid

    def _update_grid_state(self) -> None:
        pass

    def run(self):
        pass
