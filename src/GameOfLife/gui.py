import os
import re
import time
import curses
import sys
from typing import Tuple
from curses.textpad import Textbox, rectangle
import numpy as np
from GameOfLife import logger
from GameOfLife.game import Game


class Terminal_GUI:
    """
    Provides a terminal-based graphical user interface for the Game of Life.

    Attributes
    ----------
    stdscr : _CursesWindow
        The main window object provided by curses.
    no_wrapping: bool
        Determines if neighbour wrapping is applied during the game
    options : list of str
        List of options presented in the main menu.
    scr_height, scr_width : int
        Dimensions of the terminal screen.
    size_param_content, path_param_content : dict
        Dictionaries containing messages displayed during parameter selection.

    Methods
    -------
    display_main_menu(selected_row_idx)
        Displays the main menu with the current selection highlighted.
    display_param_selector(content, error=False)
        Displays an input box for parameters like grid size or file path, with an error message
        for wrong input.
    display_grid(grid)
        Displays the current state of the game grid.
    retry_size_input(size)
        Handles retrying input for grid size after format error.
    retry_path_input(path)
        Handles retrying input for file path after a file not found error.
    run_game(game)
        Starts the game loop, updating and displaying the grid continuously.
    """

    def __init__(self, stdscr, no_wrapping = False) -> None:
        self.options = [
            "Generate a random grid",
            "Grid from a file",
            "Exit the game"
        ]
        self.stdscr = stdscr
        self.no_wrapping = no_wrapping
        self.scr_height, self.scr_width = self.stdscr.getmaxyx()
        exit_msg = "Press CTRL+C to exit"
        confirmation_msg = "ENTER to confirm"
        self.size_param_content = {
            "exit": exit_msg,
            "instruction": "Enter grid size - fmt: height,width",
            "confirmation": confirmation_msg,
            "error_msg": "Wrong size format. Try again."
        }
        self.path_param_content = {
            "exit": exit_msg,
            "instruction": "Enter grid file name (in data/) - e.g. test.txt",
            "confirmation": confirmation_msg,
            "error_msg": "File not found. Try again."
        }
        self._ensure_window_size()
        curses.curs_set(0)
        # Selected menu option
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_RED,
                         curses.COLOR_BLACK)  # Error message
        logger.info("Terminal GUI initialized.")

    def _ensure_window_size(self):
        """
        Checks if the terminal window is large enough for the game; exits if not.
        """
        if self.scr_height <= 12 or self.scr_width <= 20:
            self.stdscr.clear()
            self.stdscr.addstr(
                0, 0, "Window is too small.\nPress any key to exit.")
            self.stdscr.getch()
            logger.error("Terminal window too small. Exiting.")
            sys.exit(-1)

    def _print_centered(self, y: int, text: str, attribute=None):
        """
        Utility method to print text centered on the screen.
        """
        x = self.scr_width // 2 - len(text) // 2
        if attribute:
            self.stdscr.addstr(y, x, text, attribute)
        else:
            self.stdscr.addstr(y, x, text)

    def _print_single_menu_option(self, y: int, text: str, is_selected: bool):
        """
        Prints a single menu option, highlighting if selected.
        """
        x = self.scr_width // 2 - len(text) // 2
        if is_selected:
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(y, x, text)
            self.stdscr.attroff(curses.color_pair(1))
        else:
            self.stdscr.addstr(y, x, text)

    def display_main_menu(self, selected_row_idx: int):
        """
        Displays the main menu with the specified option highlighted.

        Parameters
        ----------
        selected_row_idx : int
            Index of the currently selected menu option.
        """
        titles = {
            "main": "Welcome to the Game of Life",
            "subtitle": "By Eloi Dieme",
            "instruction": "Choose an option to start the game:"
        }

        rectangle(self.stdscr, self.scr_height // 3 - 2, self.scr_width // 2 - len(titles["instruction"]) //
                  2 - 2, self.scr_height // 3 + 9, self.scr_width // 2 + len(titles["instruction"]) // 2 + 2)

        self._print_centered(self.scr_height // 3,
                             titles["main"], attribute=curses.A_UNDERLINE)
        self._print_centered(self.scr_height // 3 + 1, titles["subtitle"])
        self._print_centered(self.scr_height // 3 + 3, titles["instruction"])

        for idx, option in enumerate(self.options):
            self._print_single_menu_option(
                self.scr_height // 3 + (5 + idx), option, is_selected=(idx == selected_row_idx))

        self.stdscr.refresh()
        logger.info("Displayed main menu.")

    def display_param_selector(self, content: dict, error: bool = False) -> str:
        """
        Displays a prompt for the user to enter parameters, such as grid size or file path,
        and error message if necessary.

        Parameters
        ----------
        content : dict
            Dictionary containing messages to display (exit, instruction, confirmation, error_msg).
        error : bool, optional
            If True, displays an error message.

        Returns
        -------
        str
            The string input by the user.
        """
        textbox_size = 30

        self.stdscr.clear()

        self.stdscr.addstr(0, 0, content["exit"])
        curses.curs_set(1)

        win = curses.newwin(1, textbox_size, self.scr_height //
                            3 + 3, self.scr_width // 2 - textbox_size // 2)
        box = Textbox(win)

        rectangle(self.stdscr, self.scr_height // 3 + 2, self.scr_width // 2 - textbox_size //
                  2 - 1, self.scr_height // 3 + 4, self.scr_width // 2 + textbox_size // 2)
        rectangle(self.stdscr, self.scr_height // 3 - 2, self.scr_width // 2 - len(content["instruction"]) //
                  2 - 2, self.scr_height // 3 + 10, self.scr_width // 2 + len(content["instruction"]) // 2 + 2)

        self._print_centered(
            self.scr_height // 3, content["instruction"], attribute=curses.A_UNDERLINE)
        self._print_centered(self.scr_height // 3 + 6,
                             content["confirmation"], attribute=curses.A_BOLD)
        if error:
            self.stdscr.attron(curses.color_pair(2))
            self._print_centered(self.scr_height // 3 +
                                 8, content["error_msg"])
            self.stdscr.attroff(curses.color_pair(2))

        def _validator(ch):
            """
            Validator function to handle special keys during input.
            """
            if ch == ord('\n'):
                return curses.ascii.BEL
            elif ch in [127, 8]:
                return curses.KEY_BACKSPACE
            return ch

        try:
            self.stdscr.refresh()
            input_str = box.edit(_validator).strip()
            return input_str
        except KeyboardInterrupt:
            logger.info("User initiated exit during parameter selection.")
            exit(0)

    def display_grid(self, grid: np.ndarray):
        """
        Displays the current state of the game grid.

        Parameters
        ----------
        grid : numpy.ndarray
            The game grid to display.
        """
        self.stdscr.addstr(0, 0, self.path_param_content["exit"])

        start_y = self.scr_height // 2 - grid.shape[0] // 2
        start_x = self.scr_width // 2 - grid.shape[1] * 2 // 2

        rectangle(self.stdscr, start_y - 1, start_x - 2, start_y +
                  grid.shape[0], start_x + grid.shape[1] * 2)

        for y in range(grid.shape[0]):
            for x in range(grid.shape[1]):
                char = 'o' if grid[y, x] == 1 else ' '
                self.stdscr.addstr(start_y + y, start_x + x * 2, char)
        logger.info("Displayed game grid.")

    def retry_size_input(self, size: str) -> Tuple[int, int]:
        """
        Continuously prompts the user to input a valid grid size after a format error,
        until a valid format is provided.

        Parameters
        ----------
        size : str
            The initial, incorrect grid size input by the user.

        Returns
        -------
        tuple
            A tuple containing the grid height and width as integers.
        """
        while True:
            self.stdscr.clear()
            size = self.display_param_selector(
                self.size_param_content, error=True)
            try:
                # Attempt to extract numeric values for grid dimensions using regex
                (grid_height, grid_width) = [int(s)
                                             for s in re.findall(r'\d+', size)]
                logger.info(
                    f"Grid size input accepted: {grid_height}x{grid_width}.")
                return (grid_height, grid_width)
            except ValueError:
                logger.error("Invalid grid size format entered.")

    def retry_path_input(self, path: str) -> str:
        """
        Continuously prompts the user for a valid file path after a file not found error,
        until an existing file path is provided.

        Parameters
        ----------
        path : str
            The initial, incorrect file path input by the user.

        Returns
        -------
        str
            The valid file path as a string.
        """
        while True:
            self.stdscr.clear()
            path = os.path.join('data', self.display_param_selector(
                self.path_param_content, error=True).strip())
            if os.path.isfile(path):
                logger.info(f"File path input accepted: {path}.")
                return path
            else:
                logger.error(f"File not found: {path}.")

    def run_game(self, game: Game):
        """
        Starts the main game loop, updating and displaying the grid state continuously
        until the user chooses to exit.

        Parameters
        ----------
        game : Game
            An instance of the Game class, used to initialize and update the game's grid state.
        """
        grid = game._initialize_grid()

        while True:
            try:
                self.stdscr.nodelay(True)  # Non-blocking mode
                key = self.stdscr.getch()
                if key == 3: #ASCII code for CTRL+C
                    logger.info("User requested exit.")
                    raise KeyboardInterrupt
                self.display_grid(grid)
                grid = game.update_grid_state(grid, self.no_wrapping)
                time.sleep(0.1)
                self.stdscr.refresh()
            except KeyboardInterrupt:
                exit(0)
            except curses.error:
                # Handle the case where the grid cannot be displayed due to screen size limitations
                self.stdscr.nodelay(False)
                self.stdscr.clear()
                error_txt = "Grid larger than the terminal screen. Press a key to exit."
                self._print_centered(self.scr_height // 2,
                                     error_txt, curses.A_REVERSE)
                logger.error(error_txt)
                key = self.stdscr.getch()
                exit(-1)
