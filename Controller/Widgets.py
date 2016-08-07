# Widgets.py.
# Gui interface files

from Tkinter import *
import threading
import time


master = Tk()

# Query the robot for a value.
# 
def query ( robot, qString ):
    robot.send(qString)
    time.sleep(.1)
    return robot.get()


# Get rid of leading '[' and trailing ']'
# Return tripplet of integers.
def stringToTriplet( string ):
    string = string.strip()
    mapValue = map (int, string[1:-1].split())
    print "Map Value %s, String %s" % (mapValue, string)
    return mapValue


class ColorBallance:
    def __init__(self, master, robot):
        self.master , self.robot = master, robot

        #frame = Frame(master, bg ='',colormap='new')
        topFrame = Frame(master)
        topFrame.pack()
        frame = Frame(topFrame)
        frame.pack()
        scroll =Frame(frame, background="tan")
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

        setValues = Button (frame, text="SetValues", 
                            command= lambda : self.setValues())
        setValues.pack(side=LEFT,expand=True)
        getValues = Button (frame, text='Get Values',
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
        time.sleep(.1)
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


class Widgets(threading.Thread):
    def __init__ (self, robot ):
        threading.Thread.__init__(self)
        self.robot = robot

    def run(self):
        master = Tk()
        cb = ColorBallance(master, self.robot)
        master.mainloop()

def initWidgets ( robot ) :
    widgets = Widgets(robot)
    return widgets




if __name__ == '__main__':
    class Robot :
        def __init__ (self):
            pass

        def send ( self, string):
            print "Robot Send String called : %s" % string 

        def get ( self) :
            print "Robot Get called "
            return "[20 30 50]"
            

    master = Tk()
    robot = Robot ()



    cb = ColorBallance( master, robot )
    # master.pack()

    master.mainloop()
