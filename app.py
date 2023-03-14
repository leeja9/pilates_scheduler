# Oregon State University
# Author: James Lee
# Course: CS 361 Winter 2023
# Assignment: Course Project
# Description: Displays Displays UI

import scheduler
from scheduler import global_var


def select_menu(menu: str) -> str:
    '''Execute selected menu functions.

    Selected function will execute and return next menu item.
    '''
    match menu:
        # 1. Startup
        case global_var.START:
            next_menu = scheduler.run_menu_start()

        # 2. Login
        case global_var.LOGIN:
            next_menu = scheduler.run_menu_login()

        case global_var.NEW_USR:
            next_menu = scheduler.run_menu_new_user()

        # 3. Main Menu
        case global_var.MAIN:
            next_menu = scheduler.run_menu_main()

        # 4. Available sessions
        case global_var.AVAIL:
            next_menu = scheduler.run_menu_sessions()

        case global_var.SEARCH:
            next_menu = scheduler.run_menu_search_sessions()

        # 5. Edit Info
        case global_var.EDIT:
            next_menu = scheduler.edit_info()

        # exit program
        case _:
            next_menu = scheduler.run_menu_exit()

    return next_menu


def run() -> None:
    '''Runs scheduling program UI'''
    scheduler.connect_db()
    menu_selection = "START"
    while menu_selection != "EXIT":
        menu_selection = select_menu(menu_selection)


if __name__ == "__main__":
    run()
