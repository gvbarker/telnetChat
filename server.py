import socket
import threading
import select
import errno

HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
lSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lSock.bind((HOSTADD, HOSTPORT))
lSock.listen(3)
clients = []
threadLock = threading.Lock()

while True:
    conn, add = lSock.accept()
    conn.sendall(b"Good")



        #def main_thread
        #create thread for every new client
        #client thread allows interaction inside the server
class serverRoom(threading.Thread):
    def __init__(self, conn, add):
        threading.Thread.__init__(self)
        self.conn = conn
        self.add = add
    def run(self):
        print(self.address + "has connected")