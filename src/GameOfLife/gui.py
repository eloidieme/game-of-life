import os
import re
import time
import curses
import sys
from curses.textpad import Textbox, rectangle

from GameOfLife import logger


class Terminal_GUI:
    def __init__(self, stdscr) -> None:
        self.options = [
            "Generate a random grid",
            "Grid from a file",
            "Exit the game"
        ]
        self.stdscr = stdscr
        self.scr_height, self.scr_width = self.stdscr.getmaxyx()
        exit_msg = "Press q to quit"
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
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    def _ensure_window_size(self):
        if self.scr_height <= 12 or self.scr_width <= 20:
            self.stdscr.clear()
            self.stdscr.addstr(
                0, 0, "Window is too small.\nPress any key to exit.")
            self.stdscr.getch()
            sys.exit(-1)

    def _print_centered(self, y, text, attribute=None):
        x = self.scr_width // 2 - len(text) // 2
        if attribute:
            self.stdscr.addstr(y, x, text, attribute)
        else:
            self.stdscr.addstr(y, x, text)

    def _print_single_menu_option(self, y, text, is_selected):
        x = self.scr_width // 2 - len(text) // 2
        if is_selected:
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(y, x, text)
            self.stdscr.attroff(curses.color_pair(1))
        else:
            self.stdscr.addstr(y, x, text)

    def display_main_menu(self, selected_row_idx):
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

    def display_param_selector(self, content, error=False):
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
            self._print_centered(self.scr_height // 3 + 8,
                                 content["error_msg"])
            self.stdscr.attroff(curses.color_pair(2))

        def _validator(ch):
            """Custom validator function to handle special keys"""
            if ch == ord('\n'):
                return curses.ascii.BEL
            elif ch == ord('q'):
                raise KeyboardInterrupt
            elif ch in [127, 8]:
                return curses.KEY_BACKSPACE
            return ch

        try:
            self.stdscr.refresh()
            input_str = box.edit(_validator)
            return input_str
        except KeyboardInterrupt:
            exit(0)

    def display_grid(self, grid):
        self.stdscr.addstr(0, 0, "Press q to quit")
        start_y = self.scr_height // 2 - grid.shape[0] // 2
        start_x = self.scr_width // 2 - grid.shape[1] * 2 // 2

        rectangle(self.stdscr, start_y - 1, start_x - 2, start_y +
                  grid.shape[0], start_x + grid.shape[1] * 2)

        for y in range(grid.shape[0]):
            for x in range(grid.shape[1]):
                char = 'o' if grid[y, x] == 1 else ' '
                self.stdscr.addstr(start_y + y, start_x + x * 2, char)

    def retry_size_input(self, size):
        while True:
            self.stdscr.clear()
            size = self.display_param_selector(
                self.size_param_content, error=True)
            try:
                (grid_height, grid_width) = [
                    int(s) for s in re.findall(r'\d+', size)]
                return (grid_height, grid_width)
            except:
                continue

    def retry_path_input(self, path):
        while True:
            self.stdscr.clear()
            path = os.path.join('data', self.display_param_selector(
                self.path_param_content, error=True).strip())
            if os.path.isfile(path):
                return path

    def run_game(self, game):
        grid = game._initialize_grid()

        while True:
            try:
                self.stdscr.nodelay(True)
                key = self.stdscr.getch()
                if key == ord('q'):
                    exit(0)
                self.display_grid(grid)
                grid = game._update_grid_state(grid)
                time.sleep(0.1)
                self.stdscr.refresh()
            except:
                self.stdscr.nodelay(False)
                self.stdscr.clear()
                error_txt = "Grid larger than the terminal screen. Press a key to exit."
                self._print_centered(self.scr_height // 2,
                                     error_txt, curses.A_REVERSE)
                logger.error(error_txt)
                key = self.stdscr.getch()
                exit(-1)
