# Oregon State University
# Author: James Lee
# Course: CS 361 Winter 2023
# Assignment: Course Project
# Description: controller for database. Executes queries


import db_conn as dbc
import datetime
from getpass import getpass
import socket
import os
from dotenv import load_dotenv
load_dotenv('./.env')

_PWHOST = os.getenv('PWHOST')
_PWPORT = int(os.getenv('PWPORT'))

# 1. STARTUP


def _welcome() -> None:
    '''
    print welcome message.
    '''
    print("Welcome to the Pilates Scheduler!")


def _select_menu(menu: str) -> str:
    '''
    run selected menu.
    '''
    match menu:
        # 1. Startup
        case "start":
            next_menu = _start_menu()

        # 2. Login
        case "login":
            next_menu = _login_menu()
        case "newusr":
            next_menu = _create_user_menu()

        # 3. Main Menu
        case "main":
            next_menu = _main_menu()

        # 4. Available sessions
        case "avail":
            next_menu = _available_sessions()
        case "search_avail":
            next_menu = _search_available()

        # exit program
        case _:
            next_menu = _exit()

    return next_menu


def _start_menu() -> str:
    '''
    Run start menu actions.
    Returns key for next menu
    '''
    opt = None
    while not (opt == 1 or opt == 2):
        print("\n--Start Menu Options--\n"
              "1. Login\n"
              "2. Create New User\n")

        opt = _get_opt()

        # quit for 'q' input
        if opt.upper() == 'Q':
            return "Q"
        elif opt.upper() == 'MAIN':
            opt = None
            continue
        try:
            opt = int(opt)
            if opt == 1:
                return "login"
            elif opt == 2:
                return "newusr"
            else:
                print("***Invalid option***")
        except Exception as e:
            if type(e) is ValueError:
                print("\n***Please enter the integer value"
                      " of the listed options***")
            else:
                print(e)


def _get_opt() -> str:
    opt = input("Please enter the integer of an option above...\n"
                "['q' for quit, 'main' for main menu]: ")
    return opt

# 2. Login


def _login_menu() -> str:
    '''
    Run login menu.
    Return key for next menu
    '''
    usr = None
    pw = None
    while (usr is None or pw is None):
        print("\n--Login Menu--\n")

        # quit for 'q' input
        usr = _get_username()
        if usr.upper() == 'Q':
            return 'Q'
        elif usr.upper() == 'MAIN':
            return 'start'
        pw = _get_pw()
        if pw.upper() == 'Q':
            return 'Q'

        try:
            name = dbc.validate_login(usr, pw)
            if name is not None:
                print("\nHi %s! How can I help you today?" % name)
                return "main"
            else:
                print("\nSorry, please try again...")
                usr = None
        except Exception as e:
            print(e)


def _create_user_menu() -> str:
    '''
    Create a new user
    '''
    usr = None
    pw = None
    while (usr is None or pw is None):
        print("\n--Create New User Menu--\n")

        # quit for 'q' input
        usr = _get_username()
        if usr.upper() == 'Q':
            return "Q"
        elif usr.upper() == 'MAIN':
            return 'start'
        pw = _get_pw()
        if pw.upper() == 'Q':
            return "Q"
        elif pw.upper() == 'MAIN':
            return "start"
        print('Please confirm password')
        pw2 = _get_pw()
        if pw2.upper() == 'Q':
            return "Q"
        elif pw2.upper() == 'MAIN':
            return 'start'
        if pw != pw2:
            print("Passwords didn't match...")
            usr = None
            continue

        try:
            status = dbc.create_user(usr, pw)
            if status[0] != "S":
                print(status)
                usr = None
            else:
                print(status)
                return "start"
        except Exception as e:
            print(e)


def _get_username() -> str:
    usr = input("Please enter your Username ('q' to quit): ")
    return usr


def _get_pw() -> str:
    pw = getpass("Please enter your Password ('q' to quit): ")
    if pw.upper() == 'Q':
        return pw
    with socket.socket() as s:
        s.connect((_PWHOST, _PWPORT))
        s.sendall(pw.encode())
        pw_hash = s.recv(1024)

    return pw_hash.decode()

# 3. Main menu


def _main_menu() -> str:
    '''
    show main menu.
    returns next menu flag
    '''
    opt = None
    while opt is None:
        print("\n--Main Menu Options--\n"
              "1. Available sessions\n"
              "     * Search for currently available sessions\n"
              "     * Book sessions if available\n"
              "2. Upcoming sessions\n"
              "     * Search for upcoming sessions you've booked\n"
              "3. Session history\n"
              "     * Search for previously attended sessions\n"
              "4. Edit personal information\n"
              "     * edit username, pw, phone, email, etc.\n"
              "5. Advanced Options (TRAINER OR ADMIN AUTHORIZATION REQUIRED)\n"
              "     * edit session lists, user authorization, etc.\n")

        opt = _get_opt_main()

        # quit for 'q' input
        if opt.upper() == 'Q':
            return "Q"
        elif opt.upper() == 'MAIN':
            opt = None
            continue
        elif opt.upper() == 'EXIT':
            return "start"

        try:
            opt = int(opt)
            match opt:
                case 1:
                    # available sessions
                    return "avail"
                case 2:
                    # upcoming sessions
                    print("coming soon!")
                    opt = None
                case 3:
                    # session history
                    print("coming soon!")
                    opt = None
                case 4:
                    # edit personal info
                    print("coming soon!")
                    opt = None
                case 5:
                    # advanced options
                    print("coming soon!")
                    opt = None
                case _:
                    print("***Invalid option***")
                    opt = None
        except Exception as e:
            if type(e) is ValueError:
                print("\n***Please enter the integer value"
                      " of the listed options***")
            else:
                print(e)


def _get_opt_main() -> str:
    '''
    Get user input for menus after login.
    '''
    opt = input("['main' to return to main menu]\n"
                "['exit' to logout of current session]\n"
                "['q' to quit program]\n"
                "Please enter the integer of an option above: ")
    return opt


# 4. Available Sessions


def _available_sessions() -> str:
    '''
    Show available sessions menu.
    Return next menu
    '''
    opt = None
    while opt is None:
        print("\n--Available Session Options--\n"
              "1. Search Available sessions\n"
              "     * Search for sessions between two dates\n"
              "2. Book Available Session\n"
              "     * Pick a day and time to book request a session\n")

        opt = _get_opt_main()

        # quit for 'q' input
        if opt.upper() == 'Q':
            return "Q"
        elif opt.upper() == 'MAIN':
            return "main"
        elif opt.upper() == 'EXIT':
            return "start"

        try:
            opt = int(opt)
            match opt:
                case 1:
                    # available sessions
                    return "search_avail"
                case 2:
                    # upcoming sessions
                    print("coming soon!")
                    opt = None
                case _:
                    print("***Invalid option***")
                    opt = None
        except Exception as e:
            if type(e) is ValueError:
                print("\n***Please enter the integer value"
                      " of the listed options***")
            else:
                print(e)


def _search_available() -> str:
    '''
    Search for available sessions between dates.
    Show list of sessions.
    Returns next menu
    '''
    opt = None
    while opt is None:
        print("\n--Search Available Sessions--\n")

        opt = _get_dates()

        # quit for 'q' input
        if opt.upper() == 'Q':
            return "Q"
        elif opt.upper() == 'MAIN':
            return "main"
        elif opt.upper() == 'EXIT':
            return "start"
        else:
            return "avail"


def _get_dates() -> str:
    '''
    get start and end dates for query
    returns next menu flag
    '''
    start_date, end_date = None, None
    while start_date is None:
        start_prompt = "Please enter a start date to search [mm/dd/yyyy]: "
        start_date = input(start_prompt)
        if start_date.upper() == 'Q':
            return "Q"
        elif start_date.upper() == 'MAIN':
            return "main"
        elif start_date.upper() == 'EXIT':
            return "start"
        end_prompt = '''Please enter an end date..\n:
        Enter a date [mm/dd/yyyy] OR number of days from start:'''
        end_date = input(end_prompt)
        if end_date.upper() == 'Q':
            return "Q"
        elif end_date.upper() == 'MAIN':
            return "main"
        elif end_date.upper() == 'EXIT':
            return "start"
        try:
            start, end = _get_date(start_date, end_date)
            if start is None:
                print("Please verify your input.")
                continue
            sessions = dbc.read_sessions((start, end))
            print("Here are the available sessions:\n")
            for session in sessions:
                print(session)
            again = input("Search another range? (y/n): ")
            if again.upper() == 'Y':
                start_date = None
                continue
            else:
                return 'avail'
        except Exception as e:
            print("Please verify your input\n%s\n" % e)
            start_date = None


def _get_date(start: str, end: str) ->\
        tuple[datetime.date, datetime.date] | tuple[None, None]:
    '''
    Validate start and end date.
    Return formated tuple or None if invalid
    '''
    try:
        date_format = '%m/%d/%Y'
        start = datetime.datetime.strptime(start, date_format).date()
        end = end.split('/')
        if len(end) == 1:
            delta = datetime.timedelta(int(end[0]))
            end = start + delta
            return (start, end)
        elif len(end) == 3:
            end = datetime.datetime.strptime('/'.join(end), date_format).date()
            return (start, end)
        else:
            return (None, None)
    except Exception as e:
        print('Error:\n%s' % e)
        return (None, None)

# MAIN LOOP


def _main_loop() -> None:
    '''
    Loop indefinitely until quit flag received
    '''
    menu = "start"
    while menu != "quit":
        menu = _select_menu(menu)


def _exit() -> str:
    '''
    Print exit statement.
    return exit flag
    '''
    print("\nExiting... Thanks for using the Pilates Scheduler!")
    return "quit"


# run the program
def run() -> None:
    dbc.init_conn()
    _welcome()
    _main_loop()
    dbc.close_conn()


if __name__ == '__main__':
    run()
