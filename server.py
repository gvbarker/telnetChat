from collections import deque
import socket
import threading
import datetime

"""
TODO: ADD ASCII ART
TODO: ADD ANSI FLAIR
TODO: FIGURE OUT THE MS TELNET ISSUES WITH ECHO SUPPRESSION
TODO: IMPLEMENT DIRECT MESSAGING SYSTEM
"""
#10.30.82.129
       
class client(threading.Thread):
    def __init__(self, conn, add):
        threading.Thread.__init__(self)
        self.conn, self.add = conn, add

    def login(self, conn, logins, connections):
        while True:
            conn.sendall(b"Please enter your login information or EXIT to cancel.\r\n")
            conn.sendall(b"USER:\r\n")
            resp = self.recAll(conn)

            #disconnect check
            if (resp==b""):
                return resp

            #back to query section
            if (resp.upper() == b"EXIT"):
                return b"EXIT"

            #no double logins
            if (resp.upper() in connections):
                conn.sendall(resp.upper() + b" is currently logged in. Please try another account.\r\n")
                continue

            #account exists 
            if (resp.upper() in logins):
                #conn.sendall(b"PASS:\r\n\xff\xfb\x01")
                conn.sendall(b"PASS:\r\n")
                resp2 = self.recAll(conn)
                print(resp2)
                resp2 = resp2.replace(b"\xFF\xFd\x01", b"")
                print(resp2)

                #validation
                if (resp2 == logins[resp.upper()]):
                    conn.sendall(b"Welcome, " + resp.upper())
                    conn.sendall(b"\r\n")
                    connections[resp.upper()] = conn
                    return resp
                else: 
                    conn.sendall(b"Invalid username-password combination.\r\n")
                    continue

            #incorrect username
            else:
                conn.sendall(b"Username not found.\r\n")


    def generateLogin(self, conn, logins, connections):
        while True:
            conn.sendall(b"Please enter a username of fewer than 16 characters or EXIT to cancel.\r\n")
            user = self.recAll(conn)

            #disconnect check
            if (user == b""):
                return user
            
            #validation
            if (user.upper() == b"EXIT"):
                return b"EXIT"
            if (len(user)>15):
                conn.sendall(b"Please enter a shorter username.\x0a\x0d")
                continue
            if (user in logins):
                conn.sendall(b"Please enter an unused username.\x0a\x0d")
                continue

            while True:
                conn.sendall(b"Please enter a case-sensitive password, and remember it!\r\nThere won't be any hints!\r\n")
                pword = self.recAll(conn).replace(b"\xFF\xFD\x01", b"")
                
                #disconnect check
                if (pword == b""):
                    return pword
                
                conn.sendall(b"Please re-enter your password for confirmation.\r\n")
                conf = self.recAll(conn).replace(b"\xFF\xFD\x01", b"")
                
                #disconnect check
                if (conf == b""):
                    return conf
                
                #validation
                if (conf != pword):
                    conn.sendall(b"Passwords do not match.\r\n")
                    continue
                conn.sendall(b"Welcome, " +  user + b"\r\n")
                logins[user.upper()]=pword
                return user
    
    def handleChatBacklog(self, conn, log, last):
        if (log[-1]!=last):
            for i in range(log.index(last), len(log)-1):
                conn.sendall(log[i][0])
                conn.sendall(b"\x0a\x0d\x0a\x0d")


    def tRecs(self, conn, user, log, lastMsg):
        received = b""
        dFlag = False
        msgReq = b"Preach it: "
        while True:
            bMsg = b""
            #chat updating
            if (lastMsg != log[-1]):
                print("updating")
                conn.send(b"\r")
                for i in range(len(received) + len(msgReq)):
                    bMsg+=b" "
                conn.send(bMsg)
                conn.send(b"\r")
                self.handleChatBacklog(conn,log, lastMsg)
                lastMsg = log[-1]
                conn.sendall(msgReq + received)
                dFlag = False

            if (dFlag):
                conn.sendall(msgReq)
                dFlag = False
            
            received += conn.recv(1024)
            eol = received.find(b"\r\n")
            
            #disconnect check
            if (received == b""):
                print("disconnect")
                tLock.acquire()
                del connections[user.upper()]
                tLock.release()
                return

            #backspace handling
            while (received.find(b"\b") != -1):
                print("backspace")
                conn.send(b"\r")
                for i in range(len(received) + len(msgReq) + 30):
                    bMsg+=b" "
                conn.sendall(bMsg)
                received = received[:len(received)-2]
                conn.send(b"\r")
                conn.sendall(msgReq +  received)

            #send handling
            if (eol != -1):
                print("sending")
                received=received[:eol]
                tLock.acquire()
                log.append((user + b": " + received, datetime.datetime.now()))
                tLock.release()
                received = b""
                dFlag = True
                #! ADD TERMINAL COMMANDS HERE
    
    def recAll(self, conn): 
        received = b""
        while True:
            #line storage
            received += conn.recv(1024)

            #disconnect check
            if (received == b""):
                return b""

            #backspace handline
            while (received.find(b"\b") != -1):
                conn.send(b"\r")
                for i in range(len(received)):
                    conn.sendall(b" ")
                received = received[:len(received)-2]
                conn.send(b"\r")
                conn.sendall(received)

            #enter-key found
            if(received.find(b"\r\n") != -1):
                return received[:received.find(b"\r\n")]


    def queryLogin(self, conn, logins, connections):
        #! ADD THE ASCII HERE 
        conn.sendall(b"Welcome to CyberBash!")
        resp = b""
        #! ADD THE ANSI CHECK/VALIDATION HERE
        while True:
            conn.sendall(b"Do you have an active login? (Y/N):\r\n")
            resp = self.recAll(conn)

            #disconnect check
            if (resp==b""):
                return b""

            #validation
            if (resp.upper() != b"Y" and resp.upper() != b"N"):
                conn.sendall(b"Please enter (Y/N).\x0a\x0d")
                continue
            if (resp.upper() == b"Y"):
                resp2 = self.login(conn, logins, connections)
                if (resp2 == b"EXIT"):
                    continue
                return resp2
            if (resp.upper() == b"N"):
                resp2 = self.generateLogin(conn, logins, connections)
                if (resp2 == b"EXIT"):
                    continue
                return resp2
    

    def run(self):
        print(self.add[0]," joined.")
        user = self.queryLogin(self.conn, logins, connections)
        
        #disconnect check
        if(user == b""):
            self.conn.close()
            print (self.add[0]," disconnected.")
            return
        
        tLock.acquire()
        connections[user.upper()]=self.conn
        tLock.release()

        msgLog.append((b"Welcome, O " + user, datetime.datetime.now()))
        lastMessage = (b"",startTime)


        input = threading.Thread(target=self.tRecs, args=(self.conn,user,msgLog, lastMessage))
        input.start()
        while True:
            if (user.upper() not in connections):
                print(user + b" disconnect")
                msgLog.append((user + b" has departed.", datetime.datetime.now()))
                break
        print("Closing ", self.add[0],"")
        self.conn.close()







HOSTADD = socket.gethostbyname(socket.gethostname())
HOSTPORT = 4444
startTime = datetime.datetime.now()
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind((HOSTADD, HOSTPORT))
listener.listen(True)
connections = {}
logins = {}
msgLog = deque([(b'',startTime)], maxlen=100)
logins[b"MASTER"] = b"master"
logins[b"T"] = b"t"
tLock = threading.Lock()
while True: 
    newconn, newadd = listener.accept()
    client(newconn,newadd).start()

