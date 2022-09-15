import socket
import threading
import select
import errno

def recAll(conn): 
    received = b""
    while True:
        received += conn.recv(1024)
        if received == b"":
            return b""
        endOfLine = received.find(b"\r\n")
        if(endOfLine != -1):
            return received[:endOfLine]

def queryUsername(conn):
     while True:
            conn.sendall(b"Please enter a username: ")
            user = recAll(conn)
            if (len(user)>15):
                conn.sendall(b"Please enter a shorter username.\x0a\x0d")
                continue
            if (user in chatters):
                conn.sendall(b"Please enter an unused username.\x0a\x0d")
                continue
            return user

#extension of the threading class
class serverRoom(threading.Thread):
    
    def __init__(self, conn, add):
        threading.Thread.__init__(self)
        self.conn = conn
        self.add = add
    def run(self):
        print(self.add + "joined")
        user = queryUsername(self.conn)
        self.conn.sendall(b"Welcome " + user)
        threadLock.acquire()
        chatters[user] = self.conn
        threadLock.release()
        while True:
            input = recAll(self.conn)
            if (input==b""):
                print(self.add + "disconnected")
                break
        self.conn.close()
        self.conn.sendall(b"Goodbye " + user)


HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(True)
chatters = {}
threadLock = threading.Lock()

while True:
    newconn, newadd = lSock.accept()
    print(newconn)
    print(newadd)
    serverRoom(newconn, newadd).start()