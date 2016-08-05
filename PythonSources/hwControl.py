import sys , os 
sys.path.append ('../MotorControl')
import isr
from Adafruit_PWM_Servo_Driver import PWM
import wiringpi as wpi
from Tokens import MyHandler
import math, numpy as np
import threading, time, math



class Distance:
    # Counts per wheel revolution.
    cpr         = 333.33
    wDiamater   = 2.5                            # Wheel diamater in inches.
    cpi         = cpr/math.pi/wDiamater          # Counts per inch.


    def __init__(self, motor ):
        (phaseA, phaseB) = (4,25) if motor else (23,24)
        self.hwIsr = isr.isr(phaseA, phaseB, motor)
        self.hwIsr.setCallback( self.callbackFn ) 

    def callbackFn ( self ) :
        print "Callback Function called"
        print "PhaseA %d, phaseB %d" % (self.hwIsr.phaseA, self.hwIsr.phaseB)

    def testCallback(self):
        self.hwIsr.testCallback()

    def getDistance(self):
        return self.hwIsr.getDistance()


class servo:
  def __init__ (self, channel, minPl, maxPl):
    self.channel, self.minPl, self.maxPl = (channel, minPl, maxPl)
    self.scale = (maxPl-minPl)/100.0

  # Input is duration in microseconds.
  def setPulseDuration( self, inDuration ):
    duration = inDuration if inDuration > self.minPl else self.minPl
    duration = duration if duration < self.maxPl else self.maxPl
    servo.pwm.setPWM ( self.channel, 0, int(round(duration/servo.tick)))

  # Input is value from to 0.0 to 100.
  def setPulsePercentage(self, inValue):
    self.setPulseDuration ( inValue*self.scale + self.minPl )

# Set class variables.
#servo.pwm = PWM(0x40, debug=True)
servo.pwm = PWM(0x40)
servo.freq = 50                                   # 20 MS pulse. 60 hz.
servo.pwm.setPWMFreq(servo.freq)                  #
servo.pulseLength = 1000000. / servo.freq
servo.tick = servo.pulseLength / 4096.0

# For tilt, 100 % points down, 0 percent points up.

servos={ 'leftTrack' : servo(0,0,8000), 'rightTrack': servo (1,0,8000),
         'pan': servo(2,1000,1800), 'tilt':servo(3,1000,2000)}


# Append servo commands.
# Key is pan, tilt, leftTrack, or rightTrack.
class hwObject:
    def __init__ ( self, key , initValue = 50):
        self.key = key 
        self.set ( initValue )
    def set( self, value ):
        if value > 100:
            value = 100
        if value < 0 :
            value = 0 
        self.value = value
        servos[self.key].setPulsePercentage(value)

    def get( self) :
        return str (self.value)

    def getValue( self):
        return self.value
    def setValue( self, value):
        #print "SetValue Key: %s, Value %d" %(self.key,  value)
        self.set(value)
 


class setHwPercent:
    def __init__ ( self, axis ):
        self.axis = axis
    def run( self,inString, tokens):
        try :
            self.axis.set ( int ( tokens[1]))
        except:
            pass
        return self.axis.get()

    def setValue( self, inValue):
        return self.axis.set(inValue)
    
class getHwPercent:
    def __init__ ( self, axis ):
        self.axis = axis
    def run( self,inString, tokens):
        return self.axis.get()

    def getValue(self):
        return self.axis.getValue()



class HBridge:
    def __init__ (self):
        isr.setup()
        isr.setDir(isr.OFF)
        self.value = 'off'
        self.cases = { 'forward': isr.FORWARD, 'reverse' :isr.BACKWARD,
                       'left': isr.LEFT, 'right':isr.RIGHT, 'off': isr.OFF,
                       'rightforward': isr.RIGHTFORWARD, 'rightbackward':isr.RIGHTBACKWARD,
                       'leftforward' : isr.LEFTFORWARD, 'leftbackward': isr.LEFTBACKWARD}


    def setValue ( self, value ):
        try:
            cmd=self.cases[value]
            self.value=value
        except:
            self.value='off'
            cmd = isr.OFF
        isr.setDir(cmd)
        return self.value
    def get( self):
        return self.value

class setGear :
    def __init__ ( self, hBridge ):
        self.hBridge = hBridge;
        
    def run ( self,inString, tokens):
        try :
            self.hBridge.setValue( tokens[1])
        except:
            pass
        return self.hBridge.get()

class getGear:
    def __init__(self, hBridge):
        self.hBridge = hBridge
    def run ( self,inString, tokens):
        return  self.hBridge.get()


class getDistance :
    def __init__ (self):
        self.right = Distance(0)
        self.left = Distance(1)
      
        
    def getValue (self ):
        dLeft = self.left.getDistance()
        dRight= self.right.getDistance()
        return np.array((dLeft, dRight))


    def run ( self,inString, tokens):
        return str (self.getValue())

# Set both motors to some value.
class motors:
    def __init__(self, left, right ):
        self.left, self.right  = left, right
    def run ( self,inString, tokens):
        try :
            speed = int(tokens[1])
            self.left.set ( speed)
            self.right.set ( speed)
        except:
            pass
        return str((self.left.value, self.right.value))

    def setValue( speed) :
        self.left.set (speed)
        self.right.set (speed)



# changeHeading
# We're stopped. Engage forward and reverse motors to change heading.

class changeHeading :

    
    ticksPerInch = 42.44
    scaleFactor = 20.0

    def __init__(self, hBridge, left, right, distance ):
        self.hBridge , self.left, self.right, self.distance   = hBridge, left, right, distance

    def setValue ( self, newValue ) :
        newValue = newValue if newValue < 180 else newValue - 360 
        scaleValue = float(newValue)/360.0*changeHeading.scaleFactor
        self.left.setValue(0)         # Turn off motors.
        self.right.setValue(0)        #
        curDistance = self.distance.getValue()
        
       
        bridgeCommand = 'left'  if newValue > 0 else 'right'
        targetDistance = curDistance + np.array(( -changeHeading.ticksPerInch, changeHeading.ticksPerInch)) * scaleValue

        # print ("Scale Value %f" % scaleValue)
        # print ("Cur Distance %s"% curDistance)
        # print ("Target  Distance %s"% targetDistance)

            
        self.hBridge.setValue(bridgeCommand)
        # Poll until we've met the conditions.
        condition = 0
        self.left.setValue (90)
        self.right.setValue(90)

   
        while condition != 3 :
            curDistance = self.distance.getValue()
            # print "Cur Distance %s Target Distance %s "% (curDistance, targetDistance)
            if bridgeCommand == 'left':
                if curDistance [0] <= targetDistance[0]:
                    #print "Condition1"
                    self.left.setValue(0)
                    condition |= 1
                if curDistance[1] >= targetDistance[1]:
                    #print "Condition2"
                    self.right.setValue(0)
                    condition|= 2
            else:
                if curDistance [0] >= targetDistance[0]:
                    #print "Condition3"
                    self.left.setValue(0)
                    condition |= 1
                if curDistance[1] <= targetDistance[1]:
                    #print "Condition 4"
                    self.right.setValue(0)
                    condition|= 2

        self.right.setValue(0)
        self.left.setValue(0)
        self.hBridge.setValue( 'off')
        
    def run ( self,inString, tokens):
        self.setValue ( int(tokens[1]))
        return "Finished"

        

class _Forward ( threading.Thread):

    ticksPerFoot = 12.0*333.33/math.pi/2.5
    def __init__(self, forward):
        threading.Thread.__init__(self)
        self.forward = forward
        self.hBridge,self.leftTrack, \
        self.rightTrack,self.distance = forward.args
        self.busy = False
        self.travelDistance = None
        self.sleepTime = 0.1

    def setDistance ( self, inDistance):
        self.travelDistance = inDistance
        deltaTick = float(inDistance) * float(_Forward.ticksPerFoot)
        self.endDistance = self.distance.getValue()+ (deltaTick,deltaTick)
        self.start()



    def run (self ):
        self.busy = True
        state = 0
        speedLeft, speedRight = 80,80 
        self.leftTrack.setValue(speedLeft)
        self.rightTrack.setValue(speedRight)
        self.hBridge.setValue('forward')
        while True:
            d = self.distance.getValue()
            dDist = self.endDistance - d
            dLeft, dRight = dDist 
            if dLeft <= 0:
                state |= 1
                self.leftTrack.setValue(0)
            if dRight<= 0:
                state |=2
                self.rightTrack.setValue(0)
            if state == 3:
                break
            time.sleep( self.sleepTime )

        self.hBridge.setValue('off')

        print "Forward Run Thread"
        time.sleep(10)
        self.busy = False
        print "Forward Thread stop"


class Forward:
    def __init__(self, hBridge,leftTrack,rightTrack,distance):
        self.args = ( hBridge,leftTrack,rightTrack,distance)
        self.forward = None
    
    def run ( self, string, tokens):
        try:
            floatVal = tokens[1]
        except:
            return "Forward No Token"

        if self.forward and self.forward.busy:
            return "Forward Busy"
            
        self.forward = _Forward(self)
        self.forward.setDistance ( floatVal)
       
        return "Forward Started"
        

def appendHwCommands( myHandler ):


    pan = hwObject('pan')
    tilt =hwObject('tilt')
    leftTrack = hwObject('leftTrack', 0)
    rightTrack= hwObject('rightTrack', 0)
    hBridge = HBridge ()
    distance = getDistance()

    myHandler.addInstance ( 'getpan', getHwPercent(pan))
    myHandler.addInstance ( 'setpan', setHwPercent(pan))
    myHandler.addInstance ( 'gettilt', getHwPercent(tilt))
    myHandler.addInstance ( 'settilt', setHwPercent(tilt))

    myHandler.addInstance ( 'getleft', getHwPercent(leftTrack))
    myHandler.addInstance ( 'setleft', setHwPercent(leftTrack))
    myHandler.addInstance ( 'getright', getHwPercent(rightTrack))
    myHandler.addInstance ( 'setright', setHwPercent(rightTrack))

    # Set the hbridge to forward, backward, spin right, spin left.
    myHandler.addInstance ( 'setgear', setGear(hBridge))
    myHandler.addInstance ( 'getgear', getGear(hBridge))
    myHandler.addInstance ('getdistance', distance )
    myHandler.addInstance ('motors', motors(leftTrack,rightTrack))
    
    # Change heading by some number of degrees ( approximated)
    # We're in a stopped state.
    myHandler.addInstance ('changeheading', changeHeading(hBridge,leftTrack,rightTrack,distance))
    myHandler.addInstance ('forward', Forward(hBridge,leftTrack,rightTrack,distance))



if __name__ == "__main__":
    import time
    import signal,sys

    def signal_handler (signal, frame ):
        servos['leftTrack'].setPulseDuration(0)
        servos['rightTrack'].setPulseDuration(0)
        isr.setDir(isr.OFF)
        servos['tilt'].setPulsePercentage(50)
        servos['pan'].setPulsePercentage(50)
        sys.exit(0)
        
    def setServos ( speedValue ) :
        servos['leftTrack'].setPulseDuration(speedValue)
        servos['rightTrack'].setPulseDuration(speedValue)

   
    servos['tilt'].setPulsePercentage(50)
    servos['pan'].setPulsePercentage(50)

    signal.signal (signal.SIGINT, signal_handler)


    isr.setup()
    isr.setDir(isr.OFF)
    speedValue = 0
    setServos (speedValue)

    #fn = 'pan'
    fn = 'tilt'
    for c in range ( 10 ) :
        for t in range ( 0,100,5 ):
            time.sleep(1)
            servos['pan'].setPulsePercentage(t)
            servos['tilt'].setPulsePercentage(t)

        for t in range ( 100,0,-5 ):
            time.sleep(1)
            servos['pan'].setPulsePercentage(t)
            servos['tilt'].setPulsePercentage(t)        



    dLeft=Distance (0)
    dRight = Distance(1)

    while True:
        cmd = raw_input ("Command , 'f','b', 'l', 'r', 's' , 'u', 'd' : ")
        cases = { 'f': (0,isr.FORWARD), 
                  'b': (0,isr.BACKWARD), 
                  'l': (0,isr.LEFT), 
                  'r': (0,isr.RIGHT), 
                  's': (0,isr.OFF),
                  'u': (1,0),
                  'd': (1,1)}
        try:
            value = cases.get( cmd[0], (0,isr.OFF))
        except:
            value=(0,isr.OFF)

        if value[0] == 0 :
            isr.setDir(value[1])
        elif value[0] == 1:
            speedValue += 1000 if value[1] == 0 else -1000
            if speedValue < 0 : speedValue = 0
            if speedValue > 10000: speedValue=10000
            setServos(speedValue)
        else:
            speedValue =0
            setServos(speedValue)
            isr.setDir(isr.OFF)

        print "Cmd is %s, speedValue %s" % ( cmd, speedValue)
        d1 = dLeft.getDistance()
        d2 = dRight.getDistance()
        print "M1 Distance %d M2: %d" % (d1, d2)


