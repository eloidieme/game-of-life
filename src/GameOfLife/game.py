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
    ) -> None:
        if grid_height <= 0 or grid_width <= 0:
            logger.error("Grid width and height must be positive.")
            raise ValueError
        
        if random_seed:
            np.random.seed(random_seed)
        
        self.grid_size = (grid_width, grid_height)
        if starting_grid_filepath:
            self.starting_grid_filepath = starting_grid_filepath
            self.random_grid = False
        else:
            self.random_grid = random_grid

    def _parse_grid_from_file(self):
        pass

    def _initialize_grid(self) -> None:
        """
        Initializes a grid using the class attributes (random or file-loaded).
        Defaults to a dead grid (meaning all the cells are set to zero).
        """
        grid = np.zeros(self.grid_size, dtype=np.bool_)

        if self.starting_grid_filepath:
            grid = self._parse_grid_from_file()

        if self.random_grid:
            grid = np.random.choice([False, True], self.grid_size)

        return grid

    def _update_grid_state(self) -> None:
        pass

    def run(self):
        pass
