import sys , os 
sys.path.append ('../MotorControl')
import isr
from Adafruit_PWM_Servo_Driver import PWM
import wiringpi as wpi
from Tokens import MyHandler




class Distance:
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


# Key is either pan or tilt.
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
        self.value = value
 


class setHwPercent:
    def __init__ ( self, axis ):
        self.axis = axis
    def run( self,inString, tokens, cf, myFrame):
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
    def run( self,inString, tokens, cf, myFrame):
        return self.axis.get()

    def getValue(self):
        return self.axis.getValue()






class HBridge:
    def __init__ (self):
        isr.setup()
        isr.setDir(isr.OFF)
        self.value = 'off'
        self.cases = { 'forward': isr.FORWARD, 'reverse' :isr.BACKWARD,
                  'left': isr.LEFT, 'right':isr.RIGHT, 'off': isr.OFF}


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
        
    def run ( self,inString, tokens, cf, myFrame):
        try :
            self.hBridge.setValue( tokens[1])
        except:
            pass
        return self.hBridge.get()

class getGear:
    def __init__(self, hBridge):
        self.hBridge = hBridge
    def run ( self,inString, tokens, cf, myFrame):
        return  self.hBridge.get()


class getDistance :
    def __init__ (self):
        self.left = Distance(0)
        self.right = Distance(1)
    def run ( self,inString, tokens, cf, myFrame):
        dLeft = self.left.getDistance()
        dRight= self.right.getDistance()
        return str ((dLeft, dRight ))

# Set both motors to some value.
class motors:
    def __init__(self, left, right ):
        self.left, self.right  = left, right
    def run ( self,inString, tokens, cf, myFrame):
        try :
            speed = int(tokens[1])
            self.left.set ( speed)
            self.right.set ( speed)
        except:
            pass
        return str((self.left.value, self.right.value))




pan = hwObject('pan')
tilt =hwObject('tilt')
leftTrack = hwObject('leftTrack', 0)
rightTrack=hwObject('rightTrack', 0)
hBridge = HBridge ()





def appendHwCommands( myHandler ):
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
    myHandler.addInstance ('getdistance', getDistance())
    myHandler.addInstance ('motors', motors(leftTrack,rightTrack))
    



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


