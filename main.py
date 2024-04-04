import curses
import re
import os

from curses import wrapper

import sys

from GameOfLife.game import Game
from GameOfLife.gui import Terminal_GUI


def main(stdscr):
    terminal = Terminal_GUI(stdscr)

    current_row_idx = 0
    terminal.display_main_menu(current_row_idx)

    home = True
    random_canvas = False
    imported_canvas = False

    while home:
        key = stdscr.getch()
        stdscr.clear()
        size = None
        path = None

        if key == curses.KEY_UP and current_row_idx > 0:
            current_row_idx -= 1
        elif key == curses.KEY_DOWN and current_row_idx < len(terminal.options) - 1:
            current_row_idx += 1
        elif (key == curses.KEY_ENTER or key in [10, 13]):
            if current_row_idx == 0:
                stdscr.clear()
                size = terminal.display_param_selector(
                    terminal.size_param_content)
                try:
                    (grid_height, grid_width) = [int(s)
                                                 for s in re.findall(r'\d+', size)]
                except ValueError:
                    (grid_height, grid_width) = terminal.retry_size_input(size)
                finally:
                    home = False
                    random_canvas = True
                    break
            elif current_row_idx == 1:
                stdscr.clear()
                path = os.path.join('data', terminal.display_param_selector(
                    terminal.path_param_content).strip())
                if not os.path.isfile(path):
                    path = terminal.retry_path_input(path)
                home = False
                imported_canvas = True
                break

            elif current_row_idx == 2:
                home = False
                sys.exit(0)

        terminal.display_main_menu(current_row_idx)

        stdscr.refresh()

    while random_canvas:
        stdscr.clear()
        curses.curs_set(0)

        game = Game(grid_height, grid_width)
        terminal.run_game(game)

    while imported_canvas:
        stdscr.clear()
        curses.curs_set(0)

        game = Game(starting_grid_filepath=path)
        terminal.run_game(game)


wrapper(main)
