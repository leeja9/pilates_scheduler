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


def book_session(client_id: int, session_id: int) -> str:
    '''Book a session'''
    qry = ("INSERT INTO SessionsDetails (clientID, instructorID, sessionID) "
           "VALUES ('%i', '1', '%i')" % (client_id, session_id))
    try:
        _cur.execute(qry)
        return "success"
    except Exception as e:
        return e


def get_upcoming_sessions(client_id: int) -> cursor.Generator:
    '''get a list of upcoming sessions for a client'''
    qry = ("SELECT "
           "Sessions.sessionID, Sessions.sessionDate, "
           "Sessions.sessionTime, Sessions.sessionLength, "
           "Sessions.sessionCapacity "
           "FROM Sessions "
           "INNER JOIN SessionsDetails "
           "ON Sessions.sessionID = SessionsDetails.sessionID "
           "AND SessionsDetails.clientID = %i" % client_id)
    try:
        _cur.execute(qry)
        return _cur
    except Exception as e:
        return e


# #######################
# CRUD: Users Table
# #######################


# CREATE
def create_user(usr: str, pw: str, auth: int, info: dict) -> str:
    '''Attempt to create user with given usr/pw.

    info description:
    info = {"fname": fname, "lname": lname,
            "email": email, "phone": phone}
    Return None if succesful.
    Return error associated with unsuccessful execution.
        Note: auth is the authorization level
        0=admin
        1=instructor
        2=client
    '''
    query = ("INSERT INTO Users (userName, password, authLvl) "
             "VALUES ('%s', '%s', '%i')" % (usr, pw, auth))
    query2 = ("SELECT userID FROM Users WHERE userName='%s'" % usr)
    try:
        _cur.execute(query)
        _cur.execute(query2)
        userid = _cur.fetchall()[0][0]
        info["userid"] = userid
        if auth == 1:
            create_instructor(info)
        else:
            create_client(info)
        return "Successfully added %s to system" % usr
    except Exception as e:
        return ("create_user() failed to add %s to system due to error...\n%s"
                % (usr, e))


# READ
def validate_login(usr: str, pw: str) -> tuple:
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

    client_id = None
    fname = None
    lname = None
    email = None
    phone = None
    if auth == 0:
        fname = usr_name
    elif auth == 1:
        query = ("SELECT * FROM Instructors "
                 "WHERE Instructors.userID='%s'" % usr_id)
        _cur.execute(query)
        fname = _cur.fetchall()
        if len(fname) == 1:
            fname = fname[0][0]
    elif auth == 2:
        query = ("SELECT * FROM Clients "
                 "WHERE Clients.userID='%s'" % usr_id)
        _cur.execute(query)
        res = _cur.fetchall()
        if len(res) == 1:
            client_id = res[0][0]
            fname = res[0][1]
            lname = res[0][2]
            email = res[0][3]
            phone = res[0][4]

    return (client_id, fname, lname, email, phone, usr_id, usr_name, auth)


def edit_info(fname: str, lname: str, email: str, phone: int,
              usr_id: int, user_name: str, client_id: int, pw: str) -> str:
    '''edit information in db'''
    try:
        if fname is not None:
            qry = ("UPDATE Clients SET firstName='%s' WHERE clientID='%i'"
                   % (fname, client_id))
            _cur.execute(qry)
            _cur.reset()
        if lname is not None:
            qry = ("UPDATE Clients SET lastName='%s' WHERE clientID='%i'"
                   % (lname, client_id))
            _cur.execute(qry)
            _cur.reset()
        if email is not None:
            qry = ("UPDATE Clients SET email='%s' WHERE clientID='%i'"
                   % (email, client_id))
            _cur.execute(qry)
            _cur.reset()
        if phone is not None:
            qry = ("UPDATE Clients SET phone='%i' WHERE clientID='%i'"
                   % (phone, client_id))
            _cur.execute(qry)
            _cur.reset()
        if user_name is not None:
            qry = ("UPDATE Users SET userName='%s' WHERE userID='%i'"
                   % (user_name, usr_id))
            _cur.execute(qry)
            _cur.reset()
        if pw is not None:
            qry = ("UPDATE Users SET password='%s' WHERE userID='%i'"
                   % (pw, usr_id))
            _cur.execute(qry)
            _cur.reset()
        return "success"
    except Exception as e:
        return e


# #######################
# CRUD: Clients Table
# #######################


# CREATE
def create_client(info: dict) -> str:
    '''Create a client in client table

    info = {"fname": fname, "lname": lname,
            "email": email, "phone": phone, "userid": userid}'''
    fname = "'%s'" % info["fname"]
    lname = "'%s'" % info["lname"] if len(info["lname"]) > 0 else "NULL"
    email = "'%s'" % info["email"]
    phone = "'%s'" % info["phone"] if len(info["phone"]) > 0 else "NULL"
    userid = "'%i'" % info["userid"]
    query = ("INSERT INTO Clients (firstName, lastName, email, phone, userID) "
             "VALUES (%s, %s, %s, %s, %s)"
             % (fname, lname, email, phone, userid))
    try:
        _cur.execute(query)
        return "Successfully added %s to system" % fname
    except Exception as e:
        return ("create_client() failed to add %s "
                "to system due to error...\n%s"
                % (fname, e))


# #######################
# CRUD: Instructors Table
# #######################


# CREATE
def create_instructor(info: dict) -> str:
    '''Create a instructor in instructor table

    info = {"fname": fname, "lname": lname,
            "email": email, "phone": phone, "userid": userid}'''
    fname = "'%s'" % info["fname"]
    lname = "'%s'" % info["lname"] if len(info["lname"]) > 0 else "NULL"
    email = "'%s'" % info["email"]
    phone = "'%s'" % info["phone"] if len(info["phone"]) > 0 else "NULL"
    userid = "'%i'" % info["userid"]
    query = ("INSERT INTO Instructors "
             "(firstName, lastName, email, phone, userID) "
             "VALUES (%s, %s, %s, %s, %s)"
             % (fname, lname, email, phone, userid))
    try:
        _cur.execute(query)
        return "Successfully added %s to system" % fname
    except Exception as e:
        return ("create_instructor() failed to add "
                "%s to system due to error...\n%s"
                % (fname, e))
