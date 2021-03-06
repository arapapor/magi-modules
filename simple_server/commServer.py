import json
import time
import logging
import socket
from threading import Thread
import threading

from magi.util import helpers


PORT=39814
BUFF=1024
FALSE=0
TXTIMEOUT=1


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG) 

ch = logging.StreamHandler()
log.addHandler(ch)

class ServerCommService:
    
    def __init__(self):
        self.active = False
        self.transportMap = dict()
        self.threadMap = dict()
        self.sock = None
    
    def initCommServer(self, replyHandler):
        functionName = self.initCommServer.__name__
        helpers.entrylog(log, functionName, level=logging.INFO)
        
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#         sock = socket.socket(socket.AF_INET, # Internet
#                              socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(TXTIMEOUT)
        self.sock.bind(('0.0.0.0', PORT))
        self.sock.listen(5)
        
        self.active = True
        thread = Thread(target=self.commServerThread,args=(replyHandler,))
        thread.start()
        
        helpers.exitlog(log, functionName, level=logging.INFO)
        return thread
    
    #Blocking, never returns
    def commServerThread(self, replyHandler):
        
        log.info("Running commServerThread on %s" % threading.currentThread().name)
        
        while self.active:
            try:
                log.info("Waiting for clients to connect.....") 
                clientsock, addr = self.sock.accept()
                time.sleep(3)
                rxdata = clientsock.recv(BUFF)
            except socket.timeout:
                continue

            try:
                jdata = json.loads(rxdata.strip())
            except:
                log.info("Exception in commServerThread while trying to parse JSON %s" % repr(rxdata))
                continue
            
            log.info("New Connection: %s" %(jdata))

            clientId = jdata['src']
            nthread = Thread(name="ServerHandler for " + str(clientId), target=self.ServerHandler, args=(clientId, clientsock, replyHandler))
            self.threadMap[clientId] = nthread
            self.transportMap[clientId] = clientsock
            nthread.start()
            
            log.info('Client %s connected.' %(clientId))
            
        log.info("Leaving commServerThread %s" % threading.currentThread().name)
        self.sock.close()
        
    #One thread is run per client on the servers's side
    def ServerHandler(self, clientId, clientsock, replyHandler):
        t = threading.currentThread()
        clientsock.settimeout(TXTIMEOUT);
        log.info("In ServerHandler Running %s" % t.name)
        
        textstring = "Hello Client " + str(clientId) + " from the server" 
        data = json.dumps({'src': 'server', 'text': textstring }) 
        self.sendOneData(clientId, data) 

        while self.active:
            try:
                rxdata = clientsock.recv(BUFF)
                log.debug("Data Received: %s" %(repr(rxdata)))
            except socket.timeout:
                log.info("Socket read failing.....")
                self.stop()
                continue
            
            try:
                jdata = json.loads(rxdata.strip())
            except :
                log.info("Exception in ServerHandler while trying to parse JSON string: %s" % repr(rxdata))
                self.stop()
                continue

            log.debug('ServerHandler RX data: %s' % repr(jdata))
            textstring = "Hello Client " + str(clientId) + " from the server" 
            data = json.dumps({'src': 'server', 'text': textstring }) 
            self.sendOneData(clientId, data) 

            #replyHandler(jdata)

        #Cleanup
        clientsock.close()
        log.info("Leaving %s" % t.name)
   

    def sendOneData(self, clientId, data):
        if clientId not in self.transportMap:
            log.error("Client %s not registered" %(clientId))
            raise Exception, "Client %s not registered" %(clientId)
            
        clientsock = self.transportMap[clientId]

        log.debug('Sending data %s' %(data))
        clientsock.send(data)

    def onerecv(self, data):
        log.info('Data is from %s' % repr(data))
        print ("** All done now **")

    def sendData(self, clientId, data):
        data['dst'] = clientId
        data = json.dumps(data)
        
        if clientId not in self.transportMap:
            log.error("Client %s not registered" %(clientId))
            raise Exception, "Client %s not registered" %(clientId)
            
        clientsock = self.transportMap[clientId]
        
        log.debug('Sending data %s' %(data))
        clientsock.send(data)
                    
    def stop(self):
        self.active = False



if __name__ == "__main__":
    server= ServerCommService()
    server.initCommServer(server.onerecv)
    time.sleep(10)
    server.stop()   
