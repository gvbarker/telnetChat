import socket
import threading
import select
import errno

def recAll(conn): 
    received = b""
    while True:
        received += conn.recv(1024)
        endOfLine = received.find(b"\r\n")
        if(endOfLine != -1):
            return received[:endOfLine]

class serverRoom(threading.Thread):
    def __init__(self, conn, add):
        threading.Thread.__init__(self)
        self.conn = conn
        self.add = add
    def run(self):
        while True:
            self.conn.sendall(b"Please enter a username: ")
            user = recAll(conn)
            if (len(user)>15):
                self.conn.sendall(b"Please enter a shorter username.\x0a\x0d")
                continue
            if (user in chatters):
                self.conn.sendall(b"Please enter an unused username.\x0a\x0d")
                continue
            self.conn.sendall(b"Welcome " + user)
            chatters[user] = add
            print(chatters)
            break

HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(3)
chatters = {}
threadLock = threading.Lock()

while True:
    conn, add = lSock.accept()
    serverRoom(conn, add).start()

