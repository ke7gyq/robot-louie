#!/usr/bin/python
# Controller.py. Provide controller gui for robot interfaces

joystickPort = '/dev/input/js0'
import cv2, math,numpy as np
import time,socket, sys, os
import threading
import pygame

import argparse

from contextlib import contextmanager


port=2000
class RobotClient (threading.Thread):
    def __init__(self, ip='happy.local', port=1857 ):
        threading.Thread.__init__(self)
        self.ip , self.port = ip,port
        self.socket = None
        self.done = False
        self.rxbuffers = list()


    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.socket.setsockopt( socket.IPPROTO_TCP,socket.TCP_NODELAY, 1)
        
    def send (self, string ):
        print ("Robot Sending String %s" %string)
        if len(string):
            sent = self.socket.send( string)
            # time.sleep(.3)
            if sent == 0 :  # Other side closed socket.
                raise RuntimeError("Socked connection Closed")

    def done(self):
        self.done= True
        
    # Return first buffer in chain, None if empty
    def get( self ) :
        if len( self.rxbuffers ):
            rv = self.rxbuffers[0]
            self.rxbuffers = self.rxbuffers[1:]
            return rv
        else:
            return None

    def run ( self ):
        f = self.socket.makefile()
        while not self.done:
            rxBuff = f.readline() 
            print "Recieved %s" % rxBuff
            if rxBuff == '':
                raise RuntimeError ("Socket Connection Closed")
            self.rxbuffers.append(rxBuff)
        self.socket.close()
            

# Class that handles the forward / reverse / left / right motoin.

class AxisMotion:
    def __init__ (self, robot=None):
        self.lr , self.ud = 0.0, 0.0
        self.robot = robot
        self.state = 'off'

    # State machine to determine direction of tracks.
    def stateTest(self, lr, ud ):
        deltaUD = self.ud -ud 
        flagUD = np.abs(deltaUD) > .1
        if self.state == 'off' and flagUD :
            if deltaUD >0:
                robot.send( 'setgear forward\n')
                self.state = 'forward'
            else:
                robot.send( 'setgear reverse\n')
                self.state = 'reverse'
        elif self.state == 'forward' and flagUD :
            if -.1 < ud < .1 :
                robot.send('setgear off')
                self.state = 'off'
            elif ud < 0:
                robot.send( 'setgear reverse\n')
                self.state = 'reverse'
        elif self.state == 'reverse' and flagUD:
            if -.1 < ud <.1 :
                robot.send('setgear off')
                self.state = 'off'
            elif ud > 0:
                robot.send('setgear forward\n')
                self.state = 'forward'

    def setVal( self, arr ):
        lr, ud = arr 
        deltaUD = ud - self.ud 
        flagUD = np.abs(deltaUD) > .1
        flagLR = np.abs(lr-self.lr) >.1
        if flagUD or flagLR:
            self.stateTest( lr,ud)             # Figure out which gear to set the robot to.
            aud = ud if ud >0 else -ud         # This is a value between 0 and 1.
            valueL = (1.0 +lr) * aud * 100.0/2
            valueR = (1.0-lr) * aud * 100.0/2
            robot.send ("setleft %d\n"%valueL)
            robot.send( "setright %d\n" % valueR)
            self.ud , self.lr = ud,lr




# Joystick handler that manages the camera.
class AxisState :
    def __init__ (self, ax1State=None, ax2State=None, robot=None, direction=(1.0,1.0)):
        self.lr, self.ud  = 0.0, 0.0
        self.dl , self.du = direction
        self.ax1State , self.ax2State, self.robot = ax1State, ax2State, robot

    def setVal( self, arr ):
        lr,ud = arr
        lr *= self.dl; ud *= self.du
        if np.abs(lr-self.lr) >.1:
            self.lr = lr
            string = "%s %d\n" %(self.ax1State, (lr + .5 ) * 100.0)
            robot.send( string ) 

        if np.abs(ud-self.ud) >.1:
            self.ud = ud
            string = "%s %d\n" %(self.ax2State, (ud + .5 ) * 100.0)
            robot.send( string ) 





class JsHandler ( threading.Thread):
    def __init__( self ):
        threading.Thread.__init__(self)
        self.actions = dict()
        self.verbose = True
        self.done = False
        self.joystick = None

    def addAction (self, key, instance):
        self.actions[ key ] =  instance

    def getAction (self, key):
        try:
            return self.actions[key]
        except:
            print "Action for Key %s not found" % key 
            return None


    def fireAction (self,key):
        instance = self.getAction( key)
        if instance:
            instance.run(self)

    # We 'know' that we only have one joystick.
    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        
        nAxis = joystick.get_numaxes()  # == 4.
        while not self.done :
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    print "Button Down  %d" %event.button
                if event.type == pygame.JOYBUTTONUP:
                    print "button Up  %d " % event.button
                if event.type == pygame.JOYHATMOTION:
                    print "Hat Motion %d %d" % event.value

            values = np.array( [ joystick.get_axis(i) for i in range ( nAxis)]).reshape(2,-1)
            self.getAction('axis1').setVal(values[0])
            self.getAction('axis2').setVal(values[1])

            clock.tick(1)
        pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Louie Control Program")
    parser.add_argument('--ipaddress', help="Robot host name", default = 'happy.local')
    parser.add_argument('--port', help = "Port Number", type=int, default ='1857')
    args = parser.parse_args()


    robot = RobotClient( args.ipaddress, args.port )
    robot.open()
    robot.start()
    
    handler = JsHandler( )
    handler.addAction ( 'axis1',  AxisMotion( robot))
    handler.addAction ( 'axis2', AxisState('setpan', 'settilt', robot, (-1.0, 1.0)))
    handler.start()

    handler.join()
    robot.run()

