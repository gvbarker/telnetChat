from multiprocessing.connection import Listener
import socket
import threading
import select
import errno

HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(3)

while True:
    conn = lSock.accept()
    conn.sendall(b"Good")