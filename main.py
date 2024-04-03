import curses
from curses import wrapper

options = [
    "Generate a random grid",
    "Load a grid from a file",
    "Create a grid with the mouse",
    "Exit the game"
]

def print_main_menu(stdscr, selected_row_idx):
    stdscr.clear()
    scr_height, scr_width = stdscr.getmaxyx()
    welcome_str = "Welcome to the Game of Life"
    subtitle = "By Eloi Dieme"
    choice = "Choose an option to start the game:"
    stdscr.addstr(scr_height // 3, scr_width // 2 - len(welcome_str) // 2, welcome_str)
    stdscr.addstr(scr_height // 3 + 1, scr_width // 2 - len(subtitle) // 2, subtitle)
    stdscr.addstr(scr_height // 3 + 3, scr_width // 2 - len(choice) // 2, choice)

    for idx, row in enumerate(options):
        y = scr_height // 3 + (idx + 5)
        x = scr_width // 2 - len(row) // 2
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row_idx = 0
    print_main_menu(stdscr, current_row_idx)
    
    stdscr.refresh()
    stdscr.getch()

wrapper(main)