# Oregon State University
# Author: James Lee
# Course: CS 361 Winter 2023
# Assignment: Course Project
# Description: controller for database. Executes queries

# Imports
import datetime
import os
from mysql import connector
from mysql.connector import cursor
from dotenv import load_dotenv
load_dotenv('./.env')   # load files from ./.env

# Global variables
_conn = connector.MySQLConnection()
_cur = cursor.MySQLCursor()


# ################
# CONNECTION SETUP
# ################

# initialize connection
def init_conn(HOST: str = os.getenv('DBHOST'),
              USER: str = os.getenv('DBUSER'),
              PW: str = os.getenv('DBPW'),
              DB: str = os.getenv('DB')) -> bool:
    '''
    initialize connection for query execution
    '''
    global _conn, _cur

    try:
        if type(HOST) is not str or\
                type(USER) is not str or\
                type(PW) is not str or\
                type(DB) is not str:
            print("args must be str type. using .env variables...")
            HOST = os.getenv('DBHOST')
            USER = os.getenv('DBUSER')
            PW = os.getenv('DBPW')
            DB = os.getenv('DB')
        if _conn.is_connected():
            close_conn()
            print('reconnecting...')
        _conn = connector.connect(host=HOST,
                                  user=USER,
                                  password=PW,
                                  database=DB,
                                  autocommit=True)
        _cur = _conn.cursor()

        print("Successfully connected to mysql server: %s@%s"
              % (USER, HOST))
        print("Using database: %s" % DB)

        return True
    except Exception as err:
        print(err)
        return False


# close connector and cursor
def close_conn() -> bool:
    '''
    Close db connector and cursor.
    Return status of closing
    '''
    global _conn, _cur
    try:
        _cur.close()
        _conn.close()
        print("Connections closed succesfully.")
        return True
    except Exception as err:
        print(err)
        return False


def change_db(DB: str) -> bool:
    '''
    change database if server connected
    '''
    global _conn, _cur
    if type(DB) is not str:
        print(str(TypeError("DB arg requires str type")))
        print("Using database: %s" % _conn.database)
    elif _conn.is_connected():
        try:
            _conn.close()
            _conn.connect(database=DB)
            _cur.close()
            _cur = _conn.cursor()
            print("Using database: %s" % DB)
        except Exception as e:
            print("Failed to connect to database.")
            print(e)
            init_conn()
    else:
        print("not connected to a server...")


# ###############
# CONTROL QUERIES
# ###############

# #######################
# CRUD: Sessions Table
# #######################

# CREATE
def create_sessions():
    # TODO
    pass


# READ
def read_sessions(filter_dates: tuple[datetime.date, datetime.date] = None,
                  filter_times: tuple[datetime.time, datetime.time] = None)\
            -> cursor.Generator:
    '''
    get list of sessions
    '''
    if filter_dates is None:
        start = datetime.date(2023, 1, 1).isoformat()
        end = datetime.date
        end = end.today().isoformat()
    else:
        start = filter_dates[0].isoformat()
        end = filter_dates[1].isoformat()
        if filter_dates[0] > filter_dates[1]:
            tmp = end
            end = start
            start = tmp

    if filter_times is None:
        start_time = datetime.time(0, 0).isoformat()
        end_time = datetime.time(23, 59).isoformat()
    else:
        start_time = filter_times[0].isoformat()
        end_time = filter_times[1].isoformat()
        if filter_times[0] > filter_times[1]:
            tmp = start_time
            start_time = end_time
            end_time = start_time
    qry = ("SELECT * FROM Sessions "
           "WHERE (sessionDate BETWEEN '%s' AND '%s') "
           "AND (sessionTime BETWEEN '%s' AND '%s')"
           % (start, end, start_time, end_time))
    _cur.execute(qry)
    return _cur


# UPDATE
def update_session():
    # TODO
    pass


# DELETE
def delete_session():
    # TODO
    pass


# #######################
# CRUD: Users Table
# #######################


# CREATE
def create_user(usr: str, pw: str, auth: int = 2) -> str:
    '''
    Attempt to create user with given usr/pw.
    Return None if succesful.
    Return error associated with unsuccessful execution.
        Note: auth is the authorization level
        0=admin
        1=instructor
        2=client
    '''
    query = ("INSERT INTO Users (userName, password, authLvl) "
             "VALUES ('%s', '%s', '%i')" % (usr, pw, auth))
    try:
        _cur.execute(query)
        return "Successfully added %s to system" % usr
    except Exception as e:
        return ("Failed to add %s to system due to error...\n%s"
                % (usr, e))


# READ
def validate_login(usr: str, pw: str) -> str:
    '''
    Validates a username and password.
    If there is a match, returns name of person.
    If no match, returns None.
    '''
    # TODO: Implement hashing for passwords
    query = ("SELECT * FROM Users "
             "WHERE userName='%s' "
             "AND password='%s'" % (usr, pw))
    _cur.execute(query)
    userlist = _cur.fetchall()
    if len(userlist) == 1:
        usr_id, usr_name, usr_pw, auth = userlist[0]
    else:
        return None

    match auth:
        case 0:
            fname = usr_name
        case 1:
            query = ("SELECT firstName FROM Instructors "
                     "WHERE Instructors.userID='%s'" % usr_id)
            _cur.execute(query)
            fname = _cur.fetchall()
            if len(fname == 1):
                fname = fname[0][0]
            else:
                fname = None
        case 2:
            query = ("SELECT firstName FROM Clients "
                     "WHERE Clients.userID='%s'" % usr_id)
            _cur.execute(query)
            fname = _cur.fetchall()
            if len(fname == 1):
                fname = fname[0][0]
            else:
                fname = None
        case _:
            fname = None

    return fname


# UPDATE
def update_user():
    # TODO
    pass


# DELETE
def delete_user():
    # TODO
    pass


# #######################
# CRUD: Clients Table
# #######################


# CREATE
def create_client():
    # TODO
    pass


# READ
def read_client():
    # TODO
    pass


# UPDATE
def update_client():
    # TODO
    pass


# DELETE
def delete_client():
    # TODO
    pass


# #######################
# CRUD: Instructors Table
# #######################


# CREATE
def create_instructor():
    # TODO
    pass


# READ
def read_instructor():
    # TODO
    pass


# UPDATE
def update_instructor():
    # TODO
    pass


# DELETE
def delete_instructor():
    # TODO
    pass


if __name__ == '__main__':
    init_conn()
    status = create_user('admin', 'test123')
    # i, name, pw, a, s = usr[0]
    print(status)
    close_conn()
