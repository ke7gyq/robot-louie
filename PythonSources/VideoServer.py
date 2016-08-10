import netifaces
import SocketServer,threading

# Network stream object.
# Open a server to send bytes to clients.


def getPreferredIp( ) :
    for myIf in ['eth0', 'wlan0' ]:
        try :
            iface = netifaces.ifaddresses( myIf).get(netifaces.AF_INET)
            if iface == None:
                continue
            print "Iface is %s" %iface
            # Assume first hardware card on interface...
            myAddress = iface[0]['addr']
            return myAddress
        except:
            raise ValueError ("No Interface found")
  

_videoServer = None


# Thread created when a new connection is made to the socket.
# The write method sends data to the client connection. (We're the server)
class ServerInstance(SocketServer.StreamRequestHandler):    
    def handle( self ) :
        _videoServer.add (self)
        while True:
            self.data = self.rfile.readline()
            if self.data == '' :
                break
        self.rfile.close()
        _videoServer.remove(self)
    def write ( self, data ):
        self.wfile.write ( data )

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# The camera calls this when it has new data to transmit to the
# attached clients. 
# Note that this is a singleton.
#
class VideoServer  :
    def __init__ ( self ):
        global _videoServer
        if _videoServer:
            raise ValueError ("Video Server already created")
        _videoServer = self
        
        self.connections = list()
        self.port = 8000
        self.host =  getPreferredIp()

        self.server = None
        self.server_thread = None
    
    # Broadcast data to connections.
    def write (self,data):
        for c in self.connections:
            try:
                c.write( data )
            except:
                pass
                
    # Remove connection from list.
    def remove ( self, connection):
        self.connections.remove (connection)

    # Add connection to list
    def add ( self, connection):
        self.connections.append(connection)


    def start ( self ):
        self.server = ThreadedTCPServer ((self.host,self.port),  ServerInstance)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon=True
        self.server_thread.start()

    # Not implemented.
    def finish ( self):
        pass

class GetVsPort:
    def __init__(self, vs ):
        self.vs = vs
    def run ( self, string , tokens ) :
        return str(self.vs.portNumber)

class SetVsPort:
    def __init__(self, vs ):
        self.vs = vs
    def run ( self, string , tokens ) :
        try:
            value = int(tokens[1])
            self.vs.portNumber = value
        except:
            pass
        return str(self.vs.portNumber)

def initVideoServer( myHandler ):
    vs = VideoServer (  ) 
    myHandler.addInstance ( 'getvsport' , GetVsPort (vs))
    myHandler.addInstance ( 'setvsport' , SetVsPort (vs))
    vs.start()
    return vs
    
    
