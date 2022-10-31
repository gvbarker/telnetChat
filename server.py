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
       
class client(threading.Thread):
    def __init__(self, conn, add, connections, logins, msgLog):
        threading.Thread.__init__(self)
        self.conn, self.add = conn, add

    def login(self, conn, logins, connections):
        while True:
            conn.sendall(b"Please enter your login information or EXIT to cancel.\r\n")
            conn.sendall(b"USER:\r\n")
            resp = self.recAll(conn,1)

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
                conn.sendall(b"PASS:\r\n")
                resp2 = self.recAll(conn,0)
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
            user = self.recAll(conn,1)

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
                pword = self.recAll(conn,0)
                
                #disconnect check
                if (pword == b""):
                    return pword

                pword = self.filterComms(pword)

                conn.sendall(b"Please re-enter your password for confirmation.\r\n")

                conf = self.recAll(conn,0)

                #disconnect check
                if (conf == b""):
                    return conf
                
                conf = self.filterComms(conf)

                #validation
                if (conf != pword):
                    conn.sendall(b"Passwords do not match.\r\n")
                    continue
                conn.sendall(b"Welcome, " +  user + b"\r\n")
                logins[user.upper()]=pword
                return user
    
    def handleChatBacklog(self, conn, log, last):
        if (last != log[-1]):
            for i in range(log.index(last)+1, len(log)):
                conn.sendall(log[i][0])
                conn.sendall(b"\r\n")
 
    def tRecs(self, conn, user, log, lastMsg):
        received = b""
        dFlag = False
        msgReq = b"Preach it: "
        while True:
            bMsg = b""
            print(lastMsg[0])
            print(log)
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
            
            lastChar = conn.recv(1024)
            received += lastChar
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
                for i in range(len(received) + len(msgReq) + 30):
                    bMsg += b" "
                print(len(bMsg), len(msgReq), len(received))
                conn.sendall(bMsg)
                received=received[:eol]
                tLock.acquire()
                log.append((user + b": " + received, datetime.datetime.now()))
                tLock.release()
                received = b""
                dFlag = True
                #! ADD TERMINAL COMMANDS HERE
                continue
            conn.send(lastChar)
    
    def recAll(self, conn, echo): 
        received = b""
        while True:
            
            #line storage
            lastChar = conn.recv(1024)
            received += lastChar

            #disconnect check
            if (received == b""):
                return b""

            received = self.filterComms(received)

            #backspace handling
            while (received.find(b"\b") != -1):
                if(len(received) == 1):
                    received = received[:0]
                    break
                conn.send(b"\r")
                for i in range(len(received)):
                    conn.sendall(b" ")
                received = received[:len(received)-2]
                conn.send(b"\r")
                conn.sendall(received)

            #enter-key found
            if(received.find(b"\r\n") != -1):
                conn.send(b"\r\n")
                return received[:received.find(b"\r\n")]
            if(echo):
                conn.send(lastChar)

    def filterComms(self, bstr):
        commands=[b"\xff\xfb\x01",b"\xff\xfd\x01",b"\xff\xfe", b"\xff\xfc",b'\xff\xfb',b'\xff\xfd',b'\xff']
        for i in commands:
            bstr = bstr.replace(i,b"")
        return bstr
        

    def queryLogin(self, conn, logins, connections):
        #entry-ascii art and welcome
        bunchaspaces = b'                   '
        fIn = open("ascii2.txt","r")
        art=fIn.read()
        art = art.split("\n")
        conn.sendall(b'\r\n')
        for i in art:
            conn.sendall(bunchaspaces)
            conn.sendall(bytes(i, 'utf-8'))
            conn.send(b"\r\n")
        conn.sendall(b'\r\n')
        conn.sendall(b"Welcome to <Bash>!")
        resp = b""
        #! ADD THE ANSI CHECK/VALIDATION HERE
        conn.send(b'\x07')
        #conn.sendall(b"\xff\xfa\x18\x")
        while True:
            conn.sendall(b"Do you have an active login? (Y/N/EXIT to close connection):\r\n")
            resp = self.recAll(conn,1)
            print(resp)

            #disconnect check
            if (resp==b""):
                return b""

            resp = resp.upper()

            #validation
            if (resp != b"Y" and resp != b"N" and resp != b"EXIT"):
                conn.sendall(b"Please enter (Y/N).\x0a\x0d")
                continue
            if (resp == b"Y"):
                resp2 = self.login(conn, logins, connections)
                if (resp2 == b"EXIT"):
                    continue
                return resp2
            if (resp == b"N"):
                resp2 = self.generateLogin(conn, logins, connections)
                if (resp2 == b"EXIT"):
                    continue
                return resp2
            if (resp == b"EXIT"):
                return b""
            
    

    def run(self):
        print(self.add[0]," joined.")
        self.conn.sendall(b'\xff\xfb\x01')
        user = self.queryLogin(self.conn, logins, connections)
        print(user)
        
        #disconnect check
        if(user == b""):
            self.conn.close()
            print (self.add[0]," disconnected.")
            return
        
        #add user to current connections
        tLock.acquire()
        connections[user.upper()]=self.conn
        tLock.release()

        #add welcome message to log
        welcome = (b"Welcome, O " + user, datetime.datetime.now())
        msgLog.append(welcome)
        lastMessage = msgLog[0]


        #enable input
        input = threading.Thread(target=self.tRecs, args=(self.conn,user,msgLog, lastMessage))
        input.start()
        while True:
            #check for disconnects
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
    client(newconn,newadd, connections, logins, msgLog).start()

