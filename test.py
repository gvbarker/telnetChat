from queue import Queue
import queue
'''
q = Queue(maxsize=6)
q.put('a')
q.put('b')
q.put('c')
q.put('d')
q.put('e')
r = Queue(maxsize=10)
print(r.queue[-1]) 
'''

'''
print (q.qsize())
print (q.queue[-1])
'''

'''
connections = {}
connections["test"] = (1,2)
print(connections["test"][0])
'''

def logShift(log, msg):
    if(not log.full()):
        log.put(msg)
        return
    log.get()
    log.put(msg)

user = b"username"
msgLog = Queue(maxsize=10)

logShift(msgLog,(user + b" has joined"))
print(msgLog.queue)