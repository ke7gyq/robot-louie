import socket
import threading
import netifaces
import time

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
  

# Not clear how to set the port number...

class VideoServer (threading.Thread):
    def __init__ (self, myHandler):
        threading.Thread.__init__(self)
        self.myHandler = myHandler
        self.maxConnections = 5
        self.portNumber = 8000
    
        self.connection = None
        self.stopFlag = False
        self.haveData = False
        self.haveConnection = False
        

    # Need to re-think this logic.
    # Note that we're giving away our connecton.
    def  run (self):
        preferredIp = getPreferredIp()
        server = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        server.bind((preferredIp, self.portNumber))
        server.listen( self.maxConnections)
  
        client, address = server.accept()


        connection = client.makefile('wb')
        self.connection = connection
        self.haveConnection = True
        while not self.stopFlag:
            #print "In Run Loop"
            # Need some form of mutex object here...
            if self.haveData:
                connection.write( data )
            time.sleep(.1)

        self.haveConnection = False
        connection.close()
        server.close()
        client.close()


    # Fixme. This really doesn't work.
    def close(self):
        self.stopFlag = True

    def write ( self, data ) :
        # print "Spooling Data for write"
        # Need mutex here.
        if self.haveConnection:
            self.connection.write (data)
            # self.data = data.copy()
            # self.haveData = True

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
    vs = VideoServer ( myHandler ) 
    myHandler.addInstance ( 'getvsport' , GetVsPort (vs))
    myHandler.addInstance ( 'setvsport' , SetVsPort (vs))
    vs.start()
    return vs
    
    
