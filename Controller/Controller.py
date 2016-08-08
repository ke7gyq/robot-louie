#!/usr/bin/python
#Contorller.py. Start Joystick and video capture on the robot.
#

from VideoClient import VideoClient
from Joystick import RobotClient,  initJsHandler
from Widgets import initWidgets
import argparse
import time




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Louie Control Program")
    parser.add_argument('--ipaddress', help="Robot host name", default = 'happy.local')
    parser.add_argument('--port', help = "Port Number", type=int, default ='1857')
    parser.add_argument('--video', help= "Real time video", default = 'y')
    parser.add_argument('--joystick', help='Enable Joystick', default='y')

    args = parser.parse_args()

    robot =  RobotClient( args.ipaddress, args.port )
    robot.open()
    robot.start()
    # Ask the robot what port number we should connect to.
    robot.send('getvsport\n')
    time.sleep(.3)
    rxStringPortNumber  = robot.get()
    # Various forms of error handling.

    if args.video=='y':
        vc = VideoClient( )
        vc.setVideoPramaters(args.ipaddress, int(rxStringPortNumber))
        vc.start()

    # Start the Joystick handler.
    if args.joystick=='y':
        jsHandler = initJsHandler( robot )
        jsHandler.start()
 


    # Start the widget handler
    widgets = initWidgets(robot)
    widgets.start()
    widgets.join()
    
    robot.join()
    if args.video:
        vc.join()

    if args.joystick:
        jsHandler.join()



