# runnable.py
import numpy as np
import cv2





class State:

    refImSize = np.array((640.0,480.0))
    halfSize = refImSize/2.0
    #halfSize = np.array((320.0, 240.0))
    pixelDeltaXY = np.array( (10.0/116.0, -10.0/112.0))*.1
    #pixelDeltaXY = np.array( (10.0/200.0, -10.0/200.0))*.1 

    def __init__(self, cf, handler):
        self.x, self.y = None, None 
        self.cf, self.handler = cf, handler

        self.panTiltTrack = True


    def inContour ( self, contour ):
        m = cv2.moments(contour)
        m00,m10,m01 = m['m00'], m['m10'], m['m01']
        x,y =  m10/m00, m01/m00
        self.x, self.y  = x,y
        self.xy = np.array((x,y), dtype=np.float)

        if self.panTiltTrack:
            panV = self.handler.getInstance('getpan').getValue()
            tiltV = self.handler.getInstance('gettilt').getValue()
            print "PanV  %d , TiltV %d X %f Y %f" %(panV, tiltV, x,y)
            imSize =self.handler.getInstance('getimagesize').getValue()
            
            dPT = (State.halfSize - self.xy)*State.pixelDeltaXY
            self.handler.getInstance('setpan').setValue(panV+dPT[0])
            self.handler.getInstance('settilt').setValue(tiltV+dPT[1])
     


class GetPosition:
    def __init__ ( self, state):
        self.state = state
    def run( self,inString, tokens, cf, myFrame):
        return str( ( self.state.x, self.state.y))
        


        

class Runnable :
    def __init__(self, string , state = None):
        self.idString = string
        self.state = state

    def run ( self, contour ) :
        self.state.inContour ( contour)
        # m = cv2.moments(contour)
        # m00,m10,m01 = (m['m00'], m['m10'], m['m01'])
        # x,y = (m10/m00, m01/m00)
        print ("Runnable String is %s" % self.idString )
        # print ("Contour length is  %s, XY %s" % (len(contour), (x,y)))





# Find the contours around a template.
# Right now,this is a hack. 
def getTemplate( inString) :
    print ("inString : %s" % inString)
    img = cv2.imread( inString )
    imGray = cv2.cvtColor( img, cv2.COLOR_BGRA2GRAY)
    _,mask = cv2.threshold( imGray, 100, 255,cv2.THRESH_BINARY)
    _,contours,heiarchy = cv2.findContours(mask.copy(),
                                            cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    return contours[3]






#
# Base directory where we keep templates.
#
templateDir = '../Templates/'

def initializeRunnable ( cf , handler ):
    state = State ( cf,handler)
    cf.addMatchTemplate ( getTemplate ( templateDir+'smallLeftTurn.png'), Runnable ('left', state) )
    cf.addMatchTemplate ( getTemplate ( templateDir+'smallRightTurn.png'), Runnable ('right', state) )
    cf.addMatchTemplate ( getTemplate ( templateDir+'smallHairpinLeft.png'), Runnable ('uTurn', state) )
    handler.addInstance('getposition', GetPosition( state))

    
