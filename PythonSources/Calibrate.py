#!/usr/bin/python
# Calibrate.py
# Play with calibration routines.

import cv2
import numpy as np

class Calibrate:
    
    def __init__(self, colConvert= cv2.COLOR_RGB2HSV):
        self.converter = colConvert
        self.sigma = 3.0

    def calibrate ( self, inImage ):
        if self.converter == cv2.COLOR_BGR2HSV:
            self.image = inImage  
        else:
            self.image= cv2.cvtColor( inImage, cv2.COLOR_RGB2BGR)

        self.imagehsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        # self.imagehsv = cv2.cvtColor(inImage, self.converter)
        cv2.imshow ('hsvImage', self.imagehsv)
        cv2.imshow ('calibrateImage', self.image)
        

        self.pointList = list()
        cv2.setMouseCallback ('calibrateImage', 
                              Calibrate.mouseCallback, self)

        
        while True:
            key = cv2.waitKey(0)
            if key == 27:
                cv2.destroyAllWindows()
                break

        points = np.array( self.pointList)

        if len(points) < 5:
            return None

        print points
        means = np.mean( points, axis=0)
        mins = np.floor(np.min(points,axis=0)).astype(np.int)
        maxs = np.ceil(np.max(points,axis=0)).astype(np.int)

        #return ( mins, maxs) 

        std  = np.std(points,axis=0)

        adjMins = np.floor(means-std*self.sigma).astype(np.int)
        adjMax =  np.ceil (means+std*self.sigma).astype(np.int)
        
        minVal = np.amax((adjMins, [0,0,0]), axis=0)
        maxVal = np.amin((adjMax , [255,255,255]),axis=0)

        return ( minVal, maxVal)

    @staticmethod
    def mouseCallback ( event, x,y, flags, self):
        if event == cv2.EVENT_LBUTTONUP:
            cHSV = self.imagehsv [ y,x,:]
            print "X: %d Y : %d %s" % (y,x,cHSV)
            self.pointList.append ( cHSV )


# Entry point from color filter.  
def doCalibrate( cf, inImage, sigma=3.0):
    calibrate = Calibrate()
    calibrate.sigma = sigma
    values = calibrate.calibrate(inImage)
    if values is not None:
        cf.lowColor, cf.highColor = values
        print "Returned Color Values %s" % str(values)
       



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Calibration Routines')
    parser.add_argument('fileName', help='Input File Name',
                        default = 'vvbgrImg.png')
    
    args = parser.parse_args()
    calibrate = Calibrate ( cv2.COLOR_BGR2HSV)
    inImage = cv2.imread ( args.fileName)
    calibrate.calibrate(inImage)
