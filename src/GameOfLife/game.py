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
    grid_size : tuple of int
        Dimensions of the grid (height, width). Inferred from grid file if None.
    random_grid : bool
        True to generate a random grid; False to load from file or initialize dead grid.
    starting_grid_filepath : str, optional
        Path to a grid file to load (.txt format with 0s and 1s).
    random_seed : int, optional
        Seed for random number generator for reproducible random grids.
    alive_probability : float
        Probability of a cell being alive at start (for random grids).

    Raises
    ------
    ValueError
        For invalid grid dimensions or missing necessary initialization parameters.
    """

    def __init__(
        self,
        grid_height: Optional[int] = None,
        grid_width: Optional[int] = None,
        random_grid: bool = True,
        starting_grid_filepath: Optional[str] = None,
        random_seed: Optional[int] = None,
        alive_probability: float = 0.5,
    ) -> None:
        if not (grid_height and grid_width) and not starting_grid_filepath:
            logger.error("Either grid dimensions or a file path must be specified.")
            raise ValueError("Grid dimensions or a file path must be provided.")

        if (grid_height and grid_width) and (grid_height <= 0 or grid_width <= 0):
            logger.error("Grid dimensions must be positive integers.")
            raise ValueError("Invalid grid dimensions provided.")

        self.grid_size = (grid_height, grid_width) if grid_height and grid_width else None
        self.random_grid = random_grid and not starting_grid_filepath
        self.starting_grid_filepath = starting_grid_filepath
        if random_seed is not None:
            np.random.seed(random_seed)
        self.alive_probability = alive_probability
        logger.info("Game initialized.")

    def _parse_grid_from_file(self) -> np.ndarray:
        """
        Reads grid configuration from a file and constructs a grid.

        Returns
        -------
        np.ndarray
            Numpy array representing the initial grid state.

        Raises
        ------
        ValueError
            If the file contains invalid characters (not 0 or 1).
        """
        file_path = Path(self.starting_grid_filepath)
        try:
            with file_path.open('r') as file:
                grid_lines = [line.strip() for line in file if line.strip()]
        except Exception as e:
            logger.error(f"Failed to read grid file: {e}")
            raise ValueError(f"Error reading grid file: {file_path}") from e

        grid = []
        for line_no, line in enumerate(grid_lines, start=1):
            row = []
            for char_no, char in enumerate(line, start=1):
                if char not in "01":
                    logger.error(f"Invalid character '{char}' at line {line_no}, column {char_no}.")
                    raise ValueError(f"Invalid character '{char}' at line {line_no}, column {char_no}.")
                row.append(int(char))
            grid.append(row)

        return np.array(grid, dtype=int)

    @staticmethod
    def _save_grid_to_file(grid: np.ndarray, path: str) -> None:
        """
        Saves the grid state to a file.

        Parameters
        ----------
        grid : np.ndarray
            The grid to save.
        path : str
            Destination file path.
        """
        try:
            np.savetxt(path, grid, fmt='%i', delimiter='')
            logger.info(f"Grid successfully saved to {path}.")
        except Exception as e:
            logger.error(f"Failed to save grid to file: {e}")
            raise

    def _initialize_grid(self) -> np.ndarray:
        """
        Initializes the grid based on the constructor parameters.

        Returns
        -------
        np.ndarray
            Initialized grid array.

        Raises
        ------
        ValueError
            If the initialization conditions are not met.
        """
        if self.starting_grid_filepath:
            return self._parse_grid_from_file()

        if self.grid_size:
            if self.random_grid:
                return np.random.choice([0, 1], size=self.grid_size, p=[1 - self.alive_probability, self.alive_probability])
            else:
                return np.zeros(self.grid_size, dtype=int)

        logger.error("Grid initialization failed due to improper configuration.")
        raise ValueError("Failed to initialize grid.")

    def update_grid_state(self, grid: np.ndarray) -> np.ndarray:
        """
        Creates the next grid from a given grid using the rules of the game:
        1. Any dead cell with exactly 3 living neighbors becomes a living cell.
        2. Any living cell with 2 or 3 living neighbors stays alive, otherwise it dies.

        Parameters
        ----------
        grid: np.ndarray
            Numpy array containing 0s and 1s corresponding to dead cells and alive cells.

        Returns
        -------
        updated_grid: np.ndarray
            Numpy array containing 0s and 1s corresponding to dead cells and alive cells, after update.
        """
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
