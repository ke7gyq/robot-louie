#!/usr/bin/python
# getSign.py

from sensors  import appendGyroCommands, getSensors
from colorFilter import ColorFilter 
from hwControl import appendHwCommands
from MsgHandler import  MsgHandler
from Tokens import getMyHandler
from Runnable import initializeRunnable
from VideoServer import initVideoServer

import cv2, numpy as np
import sys,time,socket, threading

import picamera, picamera.array





class MyFrame ( picamera.array.PiRGBAnalysis):
    def __init__ (self, camera, size):
        picamera.array.PiRGBAnalysis.__init__(self,camera,size=size)
        self.camera = camera
        self.counter = 0
        self.array = None
        self.hsvArray = None
        self.size = size
        
        self.overlayBuffer = np.zeros(  (size[1], size[0], 3),dtype=np.uint8)
        self.buf = np.getbuffer(self.overlayBuffer)
        self.overlay = camera.add_overlay( self.buf,
                                           layer=3,alpha=255 )
        
        self.colorFilter = None
        self.showHSV = False
        self.parseImage = True

    def setColorFilter ( self, colorFilter) :
        print ("Set Color Filter called")
        self.colorFilter = colorFilter


    def analyse ( self, array) :
        self.counter += 1
        self.array = array
        if self.showHSV:
            showHSVImage ( array, cv2.COLOR_RGB2HSV )

        if self.colorFilter:
            if self.parseImage:
                self.colorFilter.parseImage ( array  )
            if self.colorFilter.showMask:
                mask = self.colorFilter.maskSave
                if len(mask.shape) == 2 :
                    self.overlayBuffer[:,:,0] = mask
                    self.overlayBuffer[:,:,1] = mask
                    self.overlayBuffer[:,:,2] = mask
                else:
                    self.overlayBuffer[:,:,:] = mask
                self.overlay.update(self.buf)


# Message handlers for the camera.
# 
class GetCameraScales:
    def __init__ ( self, camera ):
        self.camera = camera
    def run( self,string, tokens ):
        rGain , bGain = self.camera.awb_gains
        iso = self.camera.iso
        return '[%f %f %f]' % (rGain, bGain, iso)
    
class SetCameraScales:
    def __init__ (self, camera):
        self.camera = camera
    def run(self,sting, tokens):
        try:
            rGain = float(tokens[1])
            bGain = float(tokens[2])
            iso   = int(tokens[3])
            
            self.camera.awb_gains = ( rGain, bGain)
            self.camera.iso = iso
        except:
            return "Could not assign camera values"
        return "Ok"


# Enale / disable the camera following an image.
class SetParseImage:
    def __init__(self, myFrame):
        self.myFrame = myFrame
    def run( self, string, tokens):
        try:
            flag = tokens[1] == 'y'
            self.myFrame.parseImage = flag
        except:
            pass
        return "%s\n" % 'y' if  self.myFrame.parseImage  else 'n'

class GetParseImage:
    def __init__(self, myFrame):
        self.myFrame = myFrame
    def run( self, string, tokens):
        return "%s\n" % 'y' if  self.myFrame.parseImage  else 'n'
     

class RecordThread ( threading.Thread ):
    def __init__(self, r264) :
        threading.Thread.__init__(self)
        self.r264 = r264
        self.busy = False
    def run (self):
        self.busy = True
        p = self.r264
        camera,filename, time = p.camera, p.filename, p.time
        print "Start Recording %s %d" %(filename, time)
        camera.start_recording(filename, format='h264', splitter_port=3)
        camera.wait_recording(time)
        camera.stop_recording(splitter_port=3)
        self.busy =False


class RecordH264:
    def __init__(self, camera):
        self.camera = camera
        self.filename, self.time = None, None
        self.RecordThread = None
    def run( self, string, tokens):
        try:
            self.filename = tokens[1]
            self.time  = int(tokens[2]) 
        except:
            return "error"
        if self.RecordThread and self.RecordThread.busy == True:
            return "busy"
            
        self.RecordThread = RecordThread( self)
        self.RecordThread.start()
        return "Recording"

            
           





def initFrameHandler( handler, myFrame):
    handler.addInstance ('setparseimage', SetParseImage(myFrame))
    handler.addInstance ('getparseimage', GetParseImage(myFrame))

def initCameraMessages( handler , camera):
    handler.addInstance('getcamerascales', GetCameraScales(camera))
    handler.addInstance('setcamerascales', SetCameraScales(camera))
    handler.addInstance('recordh264', RecordH264(camera))




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Sign Testbed")
    parser.add_argument ('--size', help='normalize to this size',   default='640 480' )
    parser.add_argument ('--showHSV', help='showHSV frame', default='n')
    parser.add_argument ('--showMask', help='Show mask option', default='n')
    parser.add_argument ('--pramFile', help='xmlPramaterFile', default='vidParms.xml')
    parser.add_argument ('--runtime', help='Running Time(sec)', type=int, default='3000')
    parser.add_argument ('--port', help = "Open server port ", type=int, default='1857')
    args = parser.parse_args()
 
    cf = ColorFilter()
    cf.xmlDecodePrams ( args.pramFile ) 


    if args.showMask == 'y': 
        cf.showMask = True
    cf.colorCvtType = cv2.COLOR_RGB2HSV
    

    # Start message handler. 
    myHandler = getMyHandler(cf)
    initializeRunnable ( cf, myHandler)
    appendHwCommands(myHandler)          # Motor contorol commands.
    appendGyroCommands(myHandler)        # Accleromater and compas.
    myHandler.fromXML ( args.pramFile )  # Read in any XLM pramaters.

    msgHandler = MsgHandler()
    vs = initVideoServer(myHandler)
    msgHandler.portNumber = args.port

    msgHandler.setHandler(myHandler)
    msgHandler.start()
    
    
    with picamera.PiCamera()  as camera:
        initCameraMessages( myHandler , camera)
        camera.resolution = (cf.imageSize )
        #camera.start_preview()
        time.sleep(2)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        camera.iso=800
        camera.awb_mode = 'off'
        camera.awb_gains = (255.0/242.0, 0)

       
        camera.start_recording(vs, format='h264', splitter_port=2)
        with MyFrame (camera, camera.resolution ) as output:
            initFrameHandler( myHandler, output)
            myHandler.myFrame  = output
            output.showHSV = args.showHSV =='y'
            output.setColorFilter(cf)
            camera.start_recording(output, 'rgb')

            camera.wait_recording(args.runtime)
            camera.stop_recording()

    sensors = getSensors()
    sensors.stop()
    msgHandler.stop()
    msgHandler.join()
    sensors.join()
    vs.join()

    print "Finished"




