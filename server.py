import socket
import threading
import select
import errno
from queue import Queue
IPCONFIG='10.30.82.30 4444'
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
    sendFlag = False
    print(list(log.queue))
    if (log.queue[-1]!=last):
        for i in log.queue:
            if (i==last):
                print("set the send flag")
                sendFlag=True
            if (sendFlag):
                print("got in the sendflag")
                print(i)
                conn.sendall(i)
                conn.sendall(b"\x0a\x0d")
                    

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

def recThread(conn, user):
    received = b""
    naiveFlag = True
    print("Made it")
    while True:
        if(naiveFlag):
            conn.sendall(b"Preach your doctrine, Wise One: ")
            naiveFlag=False
        received += conn.recv(1024)
        endOfLine = received.find(b"\r\n")
        if(endOfLine != -1):
            received=received[:endOfLine]
            threadLock.acquire()
            logShift(msgLog, (user + b": " + received))
            threadLock.release()
            received=b""
            naiveFlag=True
            continue
        if (received==b""):
            threadLock.acquire()
            print(user + " disconnected")
            logShift(msgLog,(user + b" has departed."))
            del connections[conn]
            threadLock.release()
            return

#extension of the threading class
class serverRoom(threading.Thread):

    def __init__(self, conn, add):
        threading.Thread.__init__(self)
        self.conn = conn
        self.add = add

    def run(self):
        print(self.add[0] + " joined")
        user = queryUsername(self.conn)
        threadLock.acquire()
        connections[self.conn] = (user,self.add)
        logShift(msgLog, (b"Welcome, " + user))
        lastMessage = b""
        threadLock.release()
        input = threading.Thread(target=recThread,args={self.conn,user})
        input.run()
        while True:            
            if(self.conn not in connections):
                break
            sendFlag = False
            if (msgLog.queue[-1]!=lastMessage):
                for i in msgLog.queue:
                    if (i==lastMessage):
                        print("set the send flag")
                        sendFlag=True
                    if (sendFlag):
                        print("got in the sendflag")
                        print(i)
                        self.conn.send(i)
                        self.conn.sendall(b"\x0a\x0d")

            lastMessage=msgLog.queue[-1]
        self.conn.close()


HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(True)
connections = {}
msgLog = Queue(maxsize=10)
msgLog.put(b"")
threadLock = threading.Lock()
lastMessage = b""

while True:
    newconn, newadd = lSock.accept()
    serverRoom(newconn, newadd).start()