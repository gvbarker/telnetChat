from email.errors import HeaderMissingRequiredValue
import socket
import threading
import select
import errno
from queue import Queue
def recAll(conn): 
    received = b""
    while True:
        received += conn.recv(1024)
        if received == b"":
            return b""
        endOfLine = received.find(b"\r\n")
        if(endOfLine != -1):
            return received[:endOfLine]

def handleChatBacklog(log, last, conn):
    if (log.queue[-1]!=last):
                for i in log:
                    if (log.queue[i]!=last):
                        sendFlag==True
                    if (msgLog.queue[i]!=last and sendFlag):
                        conn.sendall(i)
                    sendFlag=False
                    

def logShift(log, msg):
    if(not log.full()):
        log.put(msg)
        return
    log.get()
    log.put(msg)

def queryUsername(conn):
     while True:
            conn.sendall(b"Please enter a username: ")
            user = recAll(conn)
            if (len(user)>15):
                conn.sendall(b"Please enter a shorter username.\x0a\x0d")
                continue
            if (user in connections):
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

        threadLock.acquire()
        connections[self.conn] = (user,self.add)
        logShift(msgLog, (user + b" has joined"))
        lastMessage = user + b" has joined"
        threadLock.release()

        while True:
            handleChatBacklog(msgLog,lastMessage,self.conn)
            lastMessage=msgLog.queue[-1]
            input = recAll(self.conn)
            if (input==b""):
                threadLock.acquire()
                print(self.add + "disconnected")
                logShift(msgLog,(user + b" has departed."))
                del connections[self.conn]
                threadLock.release()
                break
            else:
                threadLock.acquire()
                logShift(msgLog, (user + b": " + input))
                lastMessage = user + b": " + input
                threadLock.release()
        self.conn.close()


HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(True)
connections = {}
msgLog = Queue(maxsize=10)
threadLock = threading.Lock()

while True:
    newconn, newadd = lSock.accept()
    print(newadd + " joined")
    serverRoom(newconn, newadd).start()