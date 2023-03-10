import socket
import hashlib
import os
import time
from dotenv import load_dotenv
load_dotenv('./.env')

HOST = os.getenv("PWHOST")
PORT = int(os.getenv("PWPORT"))
SALT = os.getenv("SALT")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print("Listening on %s:%i" % (HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                s.listen()
                conn, addr = s.accept()
                continue
            pass_change = data.decode("utf-8")
            t = time.localtime(time.time())
            print("%i-%i-%i %i:%i:%i - Password Received" %
                  (t.tm_year, t.tm_mon, t.tm_mday,
                   t.tm_hour, t.tm_min, t.tm_sec))
            salt = SALT
            salted_password = pass_change+salt
            hashed_password = hashlib.md5(salted_password.encode())
            t = time.localtime(time.time())
            print("%i-%i-%i %i:%i:%i - Hashed Password Sent" %
                  (t.tm_year, t.tm_mon, t.tm_mday,
                   t.tm_hour, t.tm_min, t.tm_sec))
            send_password = (hashed_password.hexdigest()).encode("utf-8")

            conn.sendall(send_password)
