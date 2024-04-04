import curses
import re
import time
from curses import wrapper
from curses.textpad import Textbox, rectangle
import sys

from GameOfLife.game import Game


class Terminal_GUI:
    def __init__(self, stdscr) -> None:
        self.options = [ 
            "Generate a random grid",
            "Grid from a file",
            "Exit the game"
        ]
        self.stdscr = stdscr
        self.scr_height, self.scr_width = self.stdscr.getmaxyx()
        self._ensure_window_size()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    def _ensure_window_size(self):
        if self.scr_height <= 12 or self.scr_width <= 20:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Window is too small.\nPress any key to exit.")
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
        self._print_centered(self.scr_height // 3, titles["main"], attribute=curses.A_UNDERLINE)
        self._print_centered(self.scr_height // 3 + 1, titles["subtitle"])
        self._print_centered(self.scr_height // 3 + 3, titles["instruction"])

        for idx, option in enumerate(self.options):
            self._print_single_menu_option(self.scr_height // 3 + (5 + idx), option, is_selected=(idx == selected_row_idx))

        self.stdscr.refresh()

    def display_size_selector(self, error = False):
        content = {
            "exit": "Press q to quit",
            "instruction": "Enter grid size - fmt: height,width",
            "confirmation": "ENTER to confirm",
        }
        textbox_size = 14
        
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, content["exit"])
        curses.curs_set(1)
        
        win = curses.newwin(1, textbox_size, self.scr_height // 3 + 3, self.scr_width // 2 - textbox_size // 2)
        box = Textbox(win)
        rectangle(self.stdscr, self.scr_height // 3 + 2, self.scr_width // 2 - textbox_size // 2 - 1, self.scr_height // 3 + 4, self.scr_width // 2 + textbox_size // 2)

        rectangle(self.stdscr, self.scr_height // 3 - 2, self.scr_width // 2 - len(content["instruction"]) //
                2 - 2, self.scr_height // 3 + 10, self.scr_width // 2 + len(content["instruction"]) // 2 + 2)
        self._print_centered(self.scr_height // 3, content["instruction"], attribute=curses.A_UNDERLINE)
        self._print_centered(self.scr_height // 3 + 6, content["confirmation"], attribute=curses.A_BOLD)
        if error: 
            self.stdscr.attron(curses.color_pair(2))
            self._print_centered(self.scr_height // 3 + 8, "Wrong size format. Try again.")
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
            size_str = box.edit(_validator)
            return size_str
        except KeyboardInterrupt:
            exit(0)

    def display_grid(self, grid):
        self.stdscr.addstr(0, 0, "Press q to quit")
        start_y = self.scr_height // 2 - grid.shape[0] // 2
        start_x = self.scr_width // 2 - grid.shape[1] * 2 // 2

        rectangle(self.stdscr, start_y - 1, start_x - 2, start_y + grid.shape[0], start_x + grid.shape[1] * 2)

        for y in range(grid.shape[0]):
            for x in range(grid.shape[1]):
                char = 'o' if grid[y, x] == 1 else ' '
                self.stdscr.addstr(start_y + y, start_x + x * 2, char)



def main(stdscr):
    term = Terminal_GUI(stdscr)

    current_row_idx = 0
    term.display_main_menu(current_row_idx)

    home = True
    random_canvas = False

    while home:
        key = stdscr.getch()
        stdscr.clear()
        size = None

        if key == curses.KEY_UP and current_row_idx > 0:
            current_row_idx -= 1
        elif key == curses.KEY_DOWN and current_row_idx < len(term.options) - 1:
            current_row_idx += 1
        elif (key == curses.KEY_ENTER or key in [10, 13]):
            if current_row_idx == 0:
                stdscr.clear()
                size = term.display_size_selector()
                try:
                    (grid_height, grid_width) = [int(s) for s in re.findall(r'\d+', size)]
                except ValueError:
                    wrong_input = True
                    while wrong_input:
                        stdscr.clear()
                        size = term.display_size_selector(error=True)
                        try:
                            (grid_height, grid_width) = [int(s) for s in re.findall(r'\d+', size)]
                            wrong_input = False
                        except:
                            continue
                finally:
                    home = False
                    random_canvas = True
                    break
            elif current_row_idx == len(term.options) - 1:
                home = False
                sys.exit(0)
            
        term.display_main_menu(current_row_idx)

        stdscr.refresh()

    while random_canvas:
        stdscr.clear()
        curses.curs_set(0)

        game = Game(grid_height, grid_width)
        grid = game._initialize_grid()

        while True:
            stdscr.nodelay(True)
            key = stdscr.getch()
            if key == ord('q'):
                exit(0)
            term.display_grid(grid)
            grid = game._update_grid_state(grid)
            time.sleep(0.1)
            stdscr.refresh()


wrapper(main)