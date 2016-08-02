#!/usr/bin/python

import smbus
import threading
import time

class Compass:
    def __init__ (self, baseAddr = 0x1e, busNumber=1):
        self.bus = smbus.SMBus(busNumber)
        self.addr = baseAddr

    # Write values to control registers.
    def enableDefault(self):
        values = [ 0x70,0x00, 0x00, 0x0c ]
        self.bus.write_i2c_block_data( self.addr, 0x20, values  )

    def readMagValues (self) :
        values = self.bus.read_i2c_block_data(self.addr, 0x28 ,6 )
        v = [ values[1]<<8 | values[0] , values[3] <<8 | values[2],
                 values[5]<<8 | values[4] ]
        return v
        

class Accel:
    def __init__ (self, baseAddr = 0x6b, busNumber=1):
        self.bus = smbus.SMBus(busNumber)
        self.addr = baseAddr

    def enableDefault(self):
        self.bus.write_byte_data(self.addr, 0x10, 0x80  ) # ctrl1_xl
        self.bus.write_byte_data(self.addr, 0x11, 0x80 ) # ctrl2_g
        self.bus.write_byte_data(self.addr, 0x12, 0x04 ) # ctrl3_c

    def readAccel (self):
        values = self.bus.read_i2c_block_data(self.addr, 0x28 ,6 ) #outx_l_xl
        v = [ values[1]<<8 | values[0] , values[3] <<8 | values[2],
                 values[5]<<8 | values[4] ]
        return v

    def readGyro (self):
        values = self.bus.read_i2c_block_data(self.addr, 0x22 ,6 ) #out_l_g
        v = [ values[1]<<8 | values[0] , values[3] <<8 | values[2],
                 values[5]<<8 | values[4] ]
        return v


class Sensors ( threading.Thread):
    def __init__ (self , dwellTime = 0.1 ):
        threading.Thread.__init__(self)
        self. compass = Compass ()
        self. accel = Accel()
        self.compass.enableDefault()
        self.accel.enableDefault()

        self.dwellTime = dwellTime 
        self.stopFlag = False
        
        self.magValues = None
        self.accelValues = None
        self.gyroValues = None



    def stop( self, stopFlag=True):
        self.stopFlag = stopFlag

    def run ( self ) :
        while not self.stopFlag :
            self.magValues = self.compass.readMagValues()
            self.accelValues = self.accel.readAccel()
            self.gyroValues = self.accel.readGyro()
            time.sleep( self.dwellTime)
            
    def getResultString ( self):
        return str(( self.magValues, self.accelValues, self.gyroValues))
        
    def getMag(self):
        return self.magValues
    def getAccel(self):
        return self.accelValues
    def getGyro(self):
        return self.gyroValues



class GetSensorValues:
    def __init__ (self, sensors ):
        self.sensors = sensors
        
    # This is not the thread run, but the handler for a command.
    def run ( self,inString, tokens, cf, myFrame):
        return self.sensors.getResultString()


sensors = Sensors()
sensors.start()

# Return thread for sensors.
def getSensors():
    return sensors

def appendGyroCommands (myHandler):
    myHandler.addInstance ('getsensors', GetSensorValues(sensors))



if __name__ == "__main__":
    c =compas()
    c.enableDefault()
    a=accel()
    a.enableDefault()
    while True:
        time.sleep(.1)
        print "Compas %s" % c.readMagValues()
        print "Accle Values %s "% a.readAccel()
        print "Gyro Values %s " % a.readGyro ()





