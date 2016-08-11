# Widgets.py.
# Gui interface files

from Tkinter import *
import time, sys

if not 'master' in globals():
    master = Tk()

# Query the robot for a value.
# 
def query ( robot, qString ):
    robot.send(qString)
    time.sleep(.3)
    return robot.get()


# Get rid of leading '[' and trailing ']'
# Return tripplet of integers.
def stringToTriplet( string ):
    string = string.strip()
    mapValue = map (int, string[1:-1].split())
    print "Map Value %s, String %s" % (mapValue, string)
    return mapValue

def stringToFloatTriplet(string):
    string = string.strip()
    mapValue = map (float, string[1:-1].split())
    print "Map Value %s, String %s" % (mapValue, string)
    return mapValue

class Booleans :
    def __init__(self, master, robot):
        self.master , self.robot = master, robot
        self.parseImageState = IntVar()

        topFrame = Frame (master)
        topFrame.pack()
        self.parseImage = Checkbutton ( topFrame, text = "Follow Targets", 
                                        command=self.setParseImage,
                                        variable=self.parseImageState)
        self.parseImage.pack()
        

    def setParseImage ( self ):
        print "Variable is %d" % self.parseImageState.get()

    


class CameraGains:
    def __init__(self, master, robot):
        self.master , self.robot = master, robot
    
        topFrame = Frame(master)
        topFrame.pack()
        frame = Frame(topFrame)
        frame.pack()
        scroll =Frame(frame)
        scroll.pack()


        redGain  = Scale(scroll, from_=0, to=8.0, resolution=0.01)
        redGain.pack(side=LEFT)
        blueGain = Scale(scroll,from_=0, to=8.0,resolution=0.01)
        blueGain.pack(side=LEFT)
        iso = Scale ( scroll, from_=0, to= 800,resolution=200)
        iso.pack(side=LEFT)

        setValues = Button (frame, text="Set Camera Gains", 
                            command= lambda : self.setValues())
        setValues.pack(side=LEFT,expand=True)
        getValues = Button (frame, text='Get Camera Gains',
                            command=lambda : self.getValues())
        getValues.pack(side=LEFT,expand=True)
        frame.pack()

        self.scales  = [redGain, blueGain, iso]
        self.getValues()

    def setValues(self):
        rg,bg,iso = [ v.get() for v in self.scales]
        self.robot.send("setcamerascales %f %f %d\n"% (rg,bg,iso))

    def getValues(self):
        scales = query (self.robot, 'getcamerascales\n')
        vals = stringToFloatTriplet (scales)
        for v,o in zip ( vals, self.scales):
            o.set(v)

class ColorBallance:
    def __init__(self, master, robot):
        self.master , self.robot = master, robot

        #frame = Frame(master, bg ='',colormap='new')
        topFrame = Frame(master)
        topFrame.pack()
        frame = Frame(topFrame)
        frame.pack()
        scroll =Frame(frame)
        scroll.pack()

        hueLow = Scale(scroll, from_=255, to=0)
        hueLow.pack(side=LEFT)
        hueHigh = Scale(scroll,from_=255, to=0)
        hueHigh.pack(side=LEFT)

        satLow= Scale(scroll, from_=255, to=0)
        satLow.pack(side=LEFT)
        satHigh = Scale(scroll,from_=255, to=0)
        satHigh.pack(side=LEFT)

        valLow = Scale(scroll, from_=255, to=0)
        valLow.pack(side=LEFT)
        valHigh = Scale(scroll,from_=255, to=0)
        valHigh.pack(side=LEFT)
        scroll.pack()

        setValues = Button (frame, text="Set HSV", 
                            command= lambda : self.setValues())
        setValues.pack(side=LEFT,expand=True)
        getValues = Button (frame, text='Get HSV',
                            command=lambda : self.getValues())
        getValues.pack(side=LEFT,expand=True)
        frame.pack()

        self.lowScales = [hueLow, satLow, valLow]
        self.highScales = [hueHigh, satHigh, valHigh]

        # Initialize the values from the robot.
        self.getValues()

    def setValues( self) :
        lh,ls,lv = [ v.get() for v in self.lowScales]
        hh,hs,hv = [ v.get() for v in self.highScales]
        self.robot.send( "setlow %d %d %d\n" %( lh,ls,lv ))
        time.sleep(.3)
        self.robot.send( "sethigh %d %d %d\n" %(hh,hs,hv))
        
    def getValues(self):
        low = query (self.robot, 'getlow\n')
        high = query(self.robot, 'gethigh\n')
        valsLow = stringToTriplet (low)
        valsHigh = stringToTriplet(high)
        
        for v,o in zip( valsLow, self.lowScales):
            o.set(v)
        
        for v,o in zip ( valsHigh, self.highScales):
            o.set(v)


# Note, this needs to run in the main thread.
# This is because of TK/Python restrictions
class Widgets:
    def __init__ (self, robot ):
        self.robot = robot
        
    def doClosing( self):
        print "Do Closing Called"
        master.destroy()

    def run(self):
        cb = ColorBallance(master, self.robot)
        cg = CameraGains( master, self.robot)
        cBool = Booleans(master, self.robot)
        master.protocol('WM_DELETE_WINDOW', lambda: self.doClosing() ) 
        master.mainloop()
        print "TkLoop done"

def initWidgets ( robot ) :
    widgets = Widgets(robot)
    return widgets
