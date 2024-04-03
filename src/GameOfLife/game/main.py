from pathlib import Path
from typing import Optional

import numpy as np

from GameOfLife.utils.common import parse_grid_from_file, generate_random_grid
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
        
        self.grid_size = (grid_width, grid_height)
        if starting_grid_filepath:
            self.starting_grid_filepath = starting_grid_filepath
            self.random_grid = False
        else:
            self.random_grid = random_grid
            if random_seed:
                self.random_seed = random_seed

    def _initialize_grid(self) -> None:
        """
        Initializes a grid using the class attributes (random or file-loaded).
        Defaults to a dead grid (meaning all the cells are set to zero).
        """
        grid = np.zeros(self.grid_size, dtype=np.bool_)

        if self.starting_grid_filepath:
            grid = parse_grid_from_file(self.starting_grid_filepath)

        if self.random_grid:
            grid = generate_random_grid(self.random_seed if self.random_seed else None)

        return grid

    def _update_grid_state(self) -> None:
        pass

    def run(self):
        pass
