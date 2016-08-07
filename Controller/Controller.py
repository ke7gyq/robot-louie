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
    args = parser.parse_args()

    robot =  RobotClient( args.ipaddress, args.port )
    robot.open()
    robot.start()
    # Ask the robot what port number we should connect to.
    robot.send('getvsport\n')
    time.sleep(1.0)
    rxStringPortNumber  = robot.get()
    # Various forms of error handling.
    vc = VideoClient( )
    vc.setVideoPramaters(args.ipaddress, int(rxStringPortNumber))
    vc.start()

    # Start the Joystick handler.
    jsHandler = initJsHandler( robot )
    jsHandler.start()
 


    # Start the widget handler
    widgets = initWidgets(robot)
    widgets.start()
    

    widgets.join()
    jsHandler.join()
    robot.join()
    vc.join()




