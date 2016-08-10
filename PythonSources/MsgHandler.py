import SocketServer, threading, netifaces

_MsgHandler = None

#Note that this is duplicated in videoServer.py
def getInterface () :
    for myIf in ( ['eth0', 'wlan0' ]):
        try :
            iface = netifaces.ifaddresses( myIf).get(netifaces.AF_INET)
            if iface :
                return iface[0]['addr']
        except:
            return None



# This is also duplicated in videoserver.py
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


# New thread instantiated when we receive a connect message.
class _msgHandler(SocketServer.StreamRequestHandler):
    def handle (self):
        while True:
            data = self.rfile.readline()
            if data == '' :
                self.rfile.close()
                break
            else:
                _MsgHandler.rxData ( self, data)
        

    def write ( self, data ):
                self.wfile.write ( data )



#Start thread by invoking superclass handler 'start'
class MsgHandler:
    def __init__ (self):
        global _MsgHandler
        _MsgHandler = self

        self.portNumber = 1857
        self.host = getInterface()
        self.handler = None
        self.stopFlag = False

        self.server = None
        self.server_thread = None

    # Handler needs a "run" method which is called when message arrives.
    # It reutrns a string which is sent back to the clinet.
    def setHandler ( self, handler=None):
        self.handler = handler

    def stop ( self):
        self.stopFlag = True

    def start ( self ):
        self.server = ThreadedTCPServer((self.host, self.portNumber), _msgHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

     
    def rxData (self, inHandler , inString ):
        s = inString.strip()
        if s != '' and self.handler:
            reply = self.handler.run(s)
            if reply:
                inHandler.write(reply)
