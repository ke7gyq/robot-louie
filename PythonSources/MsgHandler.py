#!/usr/bin/python

import threading
import socket
import Queue
import sys
import select
import time

import netifaces

#https://pymotw.com/2/select/


#Start thread by invoking superclass handler 'start'
class MsgHandler (threading.Thread):
    def __init__ (self):
        threading.Thread.__init__(self)
        self.portNumber = 1857
        self.setInterface ()
        self.setHandler ()
        self.verbose=False
        self.handler = None
        self.timeout = 3
        self.stopFlag = False

    # Handler needs a "run" method which is called when message arrives.
    # It reutrns a string which is sent back to the clinet.
    def setHandler ( self, handler=None):
        self.handler = handler

    def stop ( self):
        self.stopFlag = True


    def setInterface ( self ) :
        for myIf in ( ['eth0', 'wlan0' ]):
            try :
                iface = netifaces.ifaddresses( myIf).get(netifaces.AF_INET)
                # Assume first hardware card on interface...
                self.myAddress = iface[0]['addr']
                return
            except:
                pass

        raise ValueError ("No Interface found")
       
     

    def run (self):
        if self.verbose:
            print >> sys.stderr, "Run Called"
        try:
            server_address = (self.myAddress, self.portNumber)
            server= socket.socket( socket.AF_INET, socket.SOCK_STREAM)
            server.setblocking(0)
            if self.verbose:
                print >>sys.stderr, 'starting up on %s port %s' % server_address
            server.bind( server_address )
            server.listen(5)
            inputs = [server]
            outputs = []
            message_queues = {}
        except socket.error:
            print >>sys.stderr,"\nError in creating socket"
            return

        while inputs:
            if self.verbose:
                print >>sys.stderr, '\nwaiting for the next event'
            readable, writable, exceptional = select.select(inputs, outputs,inputs, self.timeout)
            if self.stopFlag:
                return


            for s in readable:
                if s is server:
                    connection, clinet_addres = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    message_queues[connection] = Queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        reply = self.handler.run ( data )
                        if reply:
                            message_queues[s].put(reply)
                            if s not in outputs:
                                outputs.append(s)
                    else:
                        # Interpret empty result as closed connection
                        #print >>sys.stderr, 'closing', client_address, 'after reading no data'
                        # Stop listening for input on the connection
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]

            # Handle outputs
            for s in writable:
                try:
                    next_msg = message_queues[s].get_nowait()
                except Queue.Empty:
                    # No messages waiting so stop checking for writability.
                    if self.verbose:
                        print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
                    outputs.remove(s)
                else:
                    if self.verbose:
                        print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
                    s.send(next_msg)


            # Handle "exceptional conditions"
            for s in exceptional:
                if self.verbose:
                    print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
                # Stop listening for input on the connection
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()

                # Remove message queue
                del message_queues[s]


if __name__ == '__main__':
    
    class MyHandler :
        def __init__(self):
            pass

        def run ( self, string ) :
            print "Recieved String ; %s"  % string
            return "DingDong"

    t = MsgHandler ()
    myHandler = MyHandler()
    t.setHandler (myHandler)
    t.start()


    while True:
        print "ding"
        time.sleep(10)
