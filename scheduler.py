# Oregon State University
# Author: James Lee
# Course: CS 361 Winter 2023
# Assignment: Course Project
# Description: Scheduler holds functions that drive the app UI

import db_conn as dbc
import datetime
from getpass import getpass
import socket
import os
from dotenv import load_dotenv
load_dotenv('./.env')


class global_var:
    '''Global variables'''
    # database connection
    PWHOST = os.getenv('PWHOST')
    PWPORT = int(os.getenv('PWPORT'))
    # global flags
    START = "START"
    LOGIN = "LOGIN"
    NEW_USR = "NEW USER"
    MAIN = "M"
    QUIT = "Q"
    AVAIL = "AVAIL"
    SEARCH = "SEARCH"
    EDIT = "EDIT"
    FLAGS_GLOBAL = (QUIT, MAIN)
    # menu options
    MENU_START = {
        1: "Login",
        2: "Create New User"
    }
    MENU_LOGIN = {}
    MENU_NEW_USR = {}
    MENU_MAIN = {
        1: "Available Sessions\n"
           "\t* Search for currently available sessions\n"
           "\t* Book sessions if available\n",
        2: "Upcoming Sessions\n"
           "\t* See upcoming sessions you've booked\n",
        3: "Edit Personal Information (CAUTION: CURRENTLY NO PW RECOVERY)\n"
           "\t* edit username, pw, phone email, etc.\n",
    }
    MENU_AVAIL = {
        1: "Search Available Sessions\n"
           "\t* Search for sessions between two dates\n"
           "\t* Book a session from generated list"
    }
    MENU_SEARCH = {}
    MENU_EDIT = {}

# Global variables used to track current user


_FNAME = None
_LNAME = None
_EMAIL = None
_PHONE = None
_USR_ID = None
_USR_NAME = None
_AUTH = None
_CLIENT_ID = None

# -------GENERAL HELPER FUNCTIONS-------


def _get_opt() -> str:
    '''Prompts user for an input an option from selected menu'''
    opt = input("Please enter the integer of an option above...\n"
                "['q'=quit, 'm'=main menu]: ")
    return opt


def _check_opt(opt: str) -> bool:
    '''Checks if user input is a universal flag

    -Converts opt to upper case.
    -Checks flag list
    '''
    check = False
    if opt.upper() in global_var.FLAGS_GLOBAL:
        check = True
    return check


def _print_menu_opts(menu_name: str, menu_items: dict) -> None:
    '''Prints menu options and items for that menu'''
    menu_display = "\n--%s Options--\n" % menu_name
    for i in range(1, len(menu_items) + 1):
        menu_display += "%i. %s\n" % (i, menu_items[i])
    print(menu_display)

# -------1. STARTUP-------


def connect_db() -> None:
    '''Initiate database connection and print welcome message.'''
    dbc.init_conn()
    print("Welcome to the Pilates Scheduler!")


def run_menu_start() -> str:
    '''
    Run start menu actions.
    Returns key for next menu
    '''
    opt = None
    while not (opt == 1 or opt == 2):
        _print_menu_opts("Start Menu", global_var.MENU_START)
        opt = _get_opt()
        if _check_opt(opt):
            if opt.upper() == 'M':
                return global_var.START
            return opt.upper()
        try:
            opt = int(opt)
            if opt == 1:
                return global_var.LOGIN
            elif opt == 2:
                return global_var.NEW_USR
            else:
                print("***Invalid option***")
        except Exception as e:
            if type(e) is ValueError:
                print("\n***Please enter the integer value"
                      " of the listed options***")
            else:
                print(e)

# -------2. LOGIN-------


def run_menu_login() -> str:
    '''
    Run login menu.
    Return key for next menu
    '''
    global _FNAME, _LNAME, _EMAIL, _PHONE
    global _USR_ID, _USR_NAME, _AUTH, _CLIENT_ID

    usr = None
    pw = None
    while (usr is None or pw is None):
        _print_menu_opts("Login Menu", global_var.MENU_LOGIN)

        # quit for 'q' input
        usr = _get_username()
        if _check_opt(usr):
            if usr.upper() == 'M':
                return global_var.START
            return usr.upper()
        pw = _get_pw()

        try:
            _CLIENT_ID, _FNAME, _LNAME, _EMAIL, _PHONE,\
                _USR_ID, _USR_NAME, _AUTH = dbc.validate_login(usr, pw)
            if _FNAME is not None:
                print("\nHi %s! How can I help you today?" % _FNAME)
                return global_var.MAIN
            else:
                print("\nSorry, please try again...")
                usr = None
        except Exception as e:
            print(e)


def run_menu_new_user() -> str:
    '''
    Create a new user
    '''
    usr = None
    pw = None
    while (usr is None or pw is None):
        _print_menu_opts("Create New User", global_var.MENU_NEW_USR)

        # get username
        usr = _get_username()
        opt = usr
        if _check_opt(opt):
            if opt.upper() == 'M':
                return global_var.START
            return opt.upper()

        # get password
        pw = _get_pw()
        opt = pw
        if _check_opt(opt):
            if opt.upper() == 'M':
                return global_var.START
            return opt.upper()

        # confirm password
        print('Please confirm password')
        pw2 = _get_pw()
        opt = pw2
        if _check_opt(opt):
            if opt.upper() == 'M':
                return global_var.START
            return opt.upper()
        if pw != pw2:
            print("Passwords didn't match...")
            usr = None
            continue

        try:
            fname = input("Please enter your first name: ")
            while len(fname) == 0:
                fname = input("Please enter your first name: ")
            lname = input("Please enter your last name (optional): ")
            email = input("Please enter your email: ")
            while not _validate_email(email):
                email = input("Please enter a valid email: ")
            phone = input("Please enter your phone number [5554443333] "
                          "(optional): ")
            while not _validate_phone(phone):
                phone = input("Please enter your phone number [5554443333] "
                              "(optional): ")
            instructor = input("Are you an instructor (y/n)? ")
            auth = 1 if instructor.lower() in ("y", "yes") else 2
            info = {"fname": fname, "lname": lname,
                    "email": email, "phone": phone}
            status = dbc.create_user(usr, pw, auth, info)
            if status[:len("Successfully")] != "Successfully":
                print(status)
                usr = None
            else:
                print(status)
                return global_var.START
        except Exception as e:
            print(e)


def _validate_email(email: str) -> bool:
    '''Validates email string'''
    if email.count('@') != 1:
        return False
    if email.split('@')[1].count('.') < 1:
        return False
    return True


def _validate_phone(phone: str) -> bool:
    '''Validates phone number string'''
    nums = [i for i in range(10)]
    if len(nums) > 0 and len(phone) != 10:
        return False
    for i in phone:
        if i not in nums:
            return False
    return True


def _get_username() -> str:
    '''Returns username input'''
    usr = input("Please enter your Username ['q'=quit, 'm'=main menu]: ")
    return usr


def _get_pw() -> str:
    '''Uses password_hash microservice to get hashed password'''
    pw = getpass("Please enter your Password ['q'=quit, 'm'=main menu]: ")
    if _check_opt(pw):
        return pw.upper()
    with socket.socket() as s:
        s.connect((global_var.PWHOST, global_var.PWPORT))
        s.sendall(pw.encode())
        pw_hash = s.recv(1024)

    return pw_hash.decode()

# -------3. MAIN MENU-------


def run_menu_main() -> str:
    '''
    show main menu.
    returns next menu flag
    '''
    opt = None
    while opt is None:
        _print_menu_opts("Main Menu", global_var.MENU_MAIN)
        opt = _get_opt()
        if _check_opt(opt):
            return opt.upper()

        try:
            opt = int(opt)
            match opt:
                case 1:
                    # available sessions
                    return global_var.AVAIL
                case 2:
                    # upcoming sessions
                    display_upcoming()
                    opt = None
                case 3:
                    # edit personal info
                    edit_info()
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

# -------4. AVAILABLE SESSIONS-------


def run_menu_sessions() -> str:
    '''
    Show available sessions menu.
    Return next menu
    '''
    opt = None
    while opt is None:
        _print_menu_opts("Available Sessions", global_var.MENU_AVAIL)
        opt = _get_opt()
        if _check_opt(opt):
            return opt.upper()
        try:
            opt = int(opt)
            match opt:
                case 1:
                    # available sessions
                    return global_var.SEARCH
                case _:
                    print("***Invalid option***")
                    opt = None
        except Exception as e:
            if type(e) is ValueError:
                print("\n***Please enter the integer value"
                      " of the listed options***")
            else:
                print(e)


def run_menu_search_sessions() -> str:
    '''
    Search for available sessions between dates.
    Show list of sessions.
    Returns next menu
    '''
    opt = None
    while opt is None:
        _print_menu_opts("Search Available Sessions", global_var.MENU_SEARCH)
        opt = _get_dates()
        if _check_opt(opt):
            return opt.upper()
        opt = input("Book a session from this list (y/n)? ")
        if _check_opt(opt):
            return opt.upper()
        if opt.upper() == 'Y':
            book_session()
        return global_var.AVAIL


def book_session() -> None:
    '''Book a session after seeing a list of available sessions'''
    session_id = input("Please enter the Session ID you'd like to book: ")
    while True:
        if _check_opt(session_id):
            break
        try:
            session_id = int(session_id)
            status = dbc.book_session(_CLIENT_ID, session_id)
            if status == "success":
                print("Successfully booked session")
            else:
                print(status)
            break
        except Exception:
            session_id = input("Please enter a valid Session ID: ")


def display_upcoming() -> None:
    '''Display a list of upcoming sessions'''
    print("\n%s, here's a list of your upcoming sessions:\n\n" % _FNAME)
    sessions = dbc.get_upcoming_sessions(_CLIENT_ID)
    _display_sessions(sessions)


def _get_dates() -> str:
    '''
    get start and end dates for query
    returns next menu flag
    '''
    start_date, end_date = None, None
    while start_date is None:
        start_prompt = "Please enter a start date to search [mm/dd/yyyy]: "
        start_date = input(start_prompt)
        opt = start_date
        if _check_opt(opt):
            return opt.upper()
        end_prompt = '''Please enter an end date..\n:
        Enter a date [mm/dd/yyyy] OR number of days from start:'''
        end_date = input(end_prompt)
        opt = end_date
        if _check_opt(opt):
            return opt.upper()
        try:
            start, end = _get_date(start_date, end_date)
            if start is None:
                print("Please verify your input.")
                continue
            sessions = dbc.read_sessions((start, end))
            print("Here are the available sessions:\n")
            _display_sessions(sessions)
            again = input("Search another range? (y/n): ")
            if again.upper() == 'Y':
                start_date = None
                continue
            else:
                return global_var.AVAIL
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


def _display_sessions(sessions: list) -> None:
    '''Print a table of session data'''
    col_length = 10
    headers = ["Session ID", "Date", "Time", "Length", "Capacity"]
    lines = "-" * (col_length * len(headers) + len(headers) + 1)
    print(lines)
    for i in range(len(headers)):
        h = headers[i]
        lpad = " " * ((col_length - len(h)) // 2)
        rpad = " " * (col_length - len(h) - len(lpad))
        headers[i] = lpad + h + rpad
    break_line = "|"
    for _ in range(len(headers)):
        break_line += '-' * col_length + "|"
    headers = "|" + "|".join(headers) + "|"
    print(headers)
    print(break_line)
    for row in sessions:
        s = "|"
        for col in row:
            lpad = " " * ((col_length - len(str(col))) // 2)
            rpad = " " * (col_length - len(str(col)) - len(lpad))
            s = s + lpad + str(col) + rpad + "|"
        print(s)
    print(lines + "\n")

# -------5. EDIT INFO-------


def edit_info() -> str:
    '''Edit user information'''
    global _FNAME, _LNAME, _EMAIL, _PHONE, _USR_ID, _USR_NAME, _CLIENT_ID
    _print_menu_opts("Edit User Information", global_var.MENU_EDIT)
    print("\nType in new information (press Enter to skip)")
    fname_prompt = "First name (current=%s): " % _FNAME
    fname = input(fname_prompt)
    fname = None if len(fname) == 0 else fname
    _FNAME = fname if fname is not None else _FNAME

    lname_prompt = "Last name (current=%s): " % _LNAME
    lname = input(lname_prompt)
    lname = None if len(lname) == 0 else lname
    _LNAME = lname if lname is not None else _LNAME

    email_prompt = "Email (current=%s): " % _EMAIL
    email = input(email_prompt)
    while len(email) > 0 and not _validate_email(email):
        print("Invalid Email")
        email = input(email_prompt)
    email = None if len(email) == 0 else email
    _EMAIL = email if email is not None else _EMAIL

    phone_prompt = "Phone (current=%i): " % _PHONE
    phone = input(phone_prompt)
    while len(phone) > 0 and not _validate_phone(phone):
        phone = input(phone_prompt)
    phone = int(phone) if len(phone) > 0 else None
    _PHONE = phone if phone is not None else _PHONE

    username_prompt = "Username (current=%s): " % _USR_NAME
    username = input(username_prompt)
    username = None if len(username) == 0 else username
    _USR_NAME = username if username is not None else _USR_NAME

    want_new_pw = input("Change pw (y/n)? ")
    pw = None
    if want_new_pw.upper() == 'Y':
        curr = getpass("Enter current password: ")
        curr = _get_pw(curr)
        check = dbc.validate_login(_USR_NAME, curr)
        while check is None:
            curr = getpass("Try again: ")
            curr = _get_pw(curr)
            check = dbc.validate_login(_USR_NAME, curr)
        pw1 = '1'
        pw2 = '2'
        while pw1 != pw2:
            pw1 = getpass("Enter new password: ")
            pw2 = getpass("Confirm new password: ")
            if pw1 != pw2:
                print("Password mismatch")
        pw = pw1
    status = dbc.edit_info(fname, lname, email, phone,
                           _USR_ID, username, _CLIENT_ID, pw)
    print("Status of update: %s" % status)
    return global_var.MAIN


# -------6. PROGRAM EXIT-------


def run_menu_exit() -> str:
    '''
    Print exit statement.
    return exit flag
    '''
    dbc.close_conn()
    print("\nExiting... Thanks for using the Pilates Scheduler!")
    return "EXIT"
