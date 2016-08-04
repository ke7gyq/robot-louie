#!/usr/bin/python
# contourTest.py.


import cv2, numpy as np
import sys
import xml.etree.ElementTree as et
from Calibrate import doCalibrate


# Convert an input string to a string of integers.
def cvtToIntegers ( inString ):
    arr = [ int(s) for s in inString.split()]
    return np.array(arr)





# First, determine if we have a match in color and outside contour.
class ColorFilter:
    defaultPoints = np.array([(50,100),(100,50), (50,0),(0,50)])
    defaultLow =(20,140,120)
    defaultHigh = (28,255,200)
    kernelSize=7
    
    #How close should we match the border ?
    borderMatchThreshold = 0.5
    symbolMatchThreshold = 0.02
    defaultMinContourLength = 10
    
    defaultImageSize =( 640, 480 )


    def __init__(self):
        self.setColorBoundries()
        self.setBorderShape()
        self.setKernel ()
        self.setMatchThreshold ()
        self.setImageSize ()
        self.setMinContourLength()
        self.matchTemplates = list()
        self.showMask = False

        self.doCalibrate = False
        self.moments = None
        self.runnable = list()
        self.pString = None                   # Base name for saving pictures.

        self.colorCvtType = cv2.COLOR_BGR2HSV
        
    def setColorBoundries (self, low=defaultLow,
                                high=defaultHigh):
        self.lowColor, self.highColor  = low, high

    def setBorderShape ( self, borderShape=defaultPoints):
        self.borderShape = borderShape
        rect = cv2.boundingRect(borderShape)
        self.templateSize = np.array([rect[2],rect[3]],dtype=np.float)

    def setKernel(self, size=kernelSize):
        self.kernelSize = size
        self.doMask = size>1
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(size,size))
        
    def setMatchThreshold (self, bmt=borderMatchThreshold,
                           smt = symbolMatchThreshold ):
        self.borderMatchThreshold, self.symbolMatchThreshold = (bmt,smt) 

    def setImageSize ( self, imgSize=defaultImageSize ) :
        self.imageSize = np.array(imgSize)

    def setMinContourLength(self, length= defaultMinContourLength):
        self.minContourLength = length



    # Contour is the contour to match, Runnable
    # is object that has a 'run' method that will be called
    # when match is found.
    # Calculate ellipse angle.
    def addMatchTemplate ( self, contour, runnable ):
        tMoment = cv2.moments(contour)
        m = [tMoment['nu30'], tMoment['nu03']]
        self.moments = [m] if self.moments is  None else  np.append(self.moments,[m], axis=0)
        self.runnable.append ( runnable )
        # self.matchTemplates.append(( m , runnable ))


    # Match the image by color values.
    # Return sets of contours associated with this image.

    def colorMatch ( self, bgrImage ):

        if self.doCalibrate:
            doCalibrate( self, bgrImage)
            self.doCalibrate = False





        hsv = cv2.cvtColor ( bgrImage, self.colorCvtType )
        mask = cv2.inRange(hsv, self.lowColor, self.highColor)
        if self.doMask:
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
            #        cv2.imshow ( 'xx', mask)
            #        cv2.waitKey(0)


        pString = self.pString
        if pString :
            bgr = cv2.cvtColor ( hsv, cv2.COLOR_HSV2BGR)
            cv2.imwrite (pString+'bgrImg.png', bgr)
            cv2.imwrite (pString+'hsvImg.png', hsv)
            cv2.imwrite (pString+'maskImg.png', mask)
            self.pString = None
            


        if self.showMask:
            self.maskSave = mask.copy()
        _,contours,heirarchy = cv2.findContours(mask, 
                                                cv2.RETR_TREE, 
                                                cv2.CHAIN_APPROX_TC89_L1 )

 
        return (contours, heirarchy)


    def parseImage ( self, bgrImage ):
        c,h = self.colorMatch(bgrImage)
        self.contours, self.heirarchy = (c,h)
        if h is None: return 
        
        print "\n"

        for cIdx, hh in enumerate (h[0]) :
            
            # m = cv2.moments(c[cIdx])
            # weight = m['m00']
            # if weight < 50:
            #     continue
            # x,y = m['m10']/weight, m['m01']/weight
            # # print "X %f , Y %f , Weight %d" %(x,y,weight) 

            # Allow 15 degree angular differences.
            mar = cv2.minAreaRect(c[cIdx])
            angle = mar[2]
            if not -60 < angle < -30:
                #print "Angle %f" % angle
                continue

            # We want a box, with a big enough size
            # to do something with. Min pixel size
            # of box = 20x20. 

            marX,marY = mar[1]
            marWeight = marX * marY 
            if marWeight < 400:   # Pixel size 20x20
               # print "Too Small area"
                continue

            marR = marY/marX
            if not .9 < marR < 1.1 :
               # print "MarX %f MarY %f, MarR %f" % (marX,marY,marR)
                continue

            if hh[2] < 0 : 
                m = cv2.moments(c[cIdx])
                weight = m['m00']
                x,y = m['m10']/weight, m['m01']/weight
                absWeight = np.abs(weight - marWeight) / marWeight
                if .9 < absWeight < 1.1 :
                    print "Likely Target at  x %f, y %f, Weight %f" %(x,y,weight)
                continue


        
            #print mar

            # # Test top level to make sure that we're looking at a square shape.
            # matchScore  = cv2.matchShapes( self.borderShape, c[cIdx], 1,0)
            # #print ("Match Score is %f" % matchScore)


            # if matchScore > self.borderMatchThreshold: 
            #     continue
            cc = c[hh[2]]

            # This is a "have sign" case.
            if len(cc) < self.minContourLength:
                print "Not enough points in contour %d"% len(cc)
                m = cv2.moments(c[cIdx])
                weight = m['m00']
                x,y = m['m10']/weight, m['m01']/weight
                absWeight = np.abs(weight - marWeight) / marWeight
                #if .9 < absWeight < 1.1 :
                print "Likely Target at  x %f, y %f, Weight %f" %(x,y,weight)

                continue


            moments = cv2.moments( cc )
            m = np.array((moments['nu30'], moments['nu03']))
            # print "Normalized Central Moments : %f %f" % (moments['nu30'], moments['nu03'])
            scores = np.linalg.norm ( self.moments - m , axis = 1)

            idxMin = np.argmin ( scores ) 
            minMatch = scores[idxMin] 
            # print "MinMatch is %f" % minMatch
            # Note, We're sending in the bounding box for the symbol.
            if minMatch < self.symbolMatchThreshold:
                self.runnable[idxMin].run (c[cIdx])
           

    # Debugging function.
    def showPoints ( self,  inPoints ) :
        rect = cv2.boundingRect ( inPoints)
        img = np.zeros ((rect[2],rect[3]))
        inPoints [:,:,0] -= rect[0]
        inPoints[:,:,1] -= rect[1]
        img = cv2.drawContours(img, [inPoints], -1, 255)
        cv2.imshow('Img', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # This needs to go away.
    def xmlDecodePrams ( self,inFileName ):
        try:
            tree = et.parse(inFileName)
            root = tree.getroot()
        except:
            print "Could not open %s" % inFileName
            print "Using Defaults"
            return
        print "Decoded %s" % inFileName
        if root.tag == 'parms':
            for cf in  root.iter('colorFilter'):
                for item in cf:
                    self.decodeTag( item.tag, item.attrib)


    
    # This needs to go away.
    def decodeTag( self, tag, attrib ) :
        if tag == 'colorRange':
            lowColor = cvtToIntegers( attrib['lowColor'])
            highColor =cvtToIntegers( attrib['highColor'])
            self.setColorBoundries ( lowColor, highColor)
        if tag  == 'templateShape':
            values = cvtToIntegers( attrib['value'])
            points = np.array( values)
            points.shape = (4,2)
            self.setBorderShape( points) 
        if tag == 'kernelSize':
            value = int(attrib['value'])
            self.setKernel(value)
        if tag == 'thresholds':
            borderMatch = float(attrib['borderMatch'])
            symbolMatch = float(attrib['symbolMatch'])
            self.setMatchThreshold( borderMatch, symbolMatch)
        if tag == 'imageSize':
            self.imageSize = cvtToIntegers( attrib['value'])
        if tag == 'minContourLength':
            self.setMinContourLength(int(attrib['value']))



if __name__ == '__main__':
    import argparse
    def mouseCallback(event,x,y,flags,hsv):
        if event == cv2.EVENT_LBUTTONUP:
            cHSV = hsv[y,x,:]
            print "X,Y %d %d %s " % (x,y, cHSV)


    def showHSVImage ( inImage , colorFilter = cv2.COLOR_BGR2HSV ) :
        if colorFilter == cv2.COLOR_BGR2HSV:
            cv2.imshow ( 'bgr', inImage)
        else:
            ii = cv2.cvtColor(inImage, cv2.COLOR_RGB2BGR)
            cv2.imshow ( 'rgb', ii)

        hsv = cv2.cvtColor(inImage, colorFilter )
        cv2.imshow ( 'hsv', hsv)
        cv2.setMouseCallback('bgr', mouseCallback, hsv)

        while True:
            if cv2.waitKey(0) & 0xff == 27:
                cv2.destroyAllWindows()
                return


    def showHSV ( inFileName ) :
        bgr = cv2.imread( inFileName )
        showHSVImage ( bgr )
   

    # Find the contours around a template.
    # Right now,this is a hack. 
    # Note that this code is duplicated in runnable.py
    def getTemplate( inString) :
        print ("inString : %s" % inString)
        img = cv2.imread( inString )
        imGray = cv2.cvtColor( img, cv2.COLOR_BGRA2GRAY)
        _,mask = cv2.threshold( imGray, 100, 255,cv2.THRESH_BINARY)
        _,contours,heiarchy = cv2.findContours(mask.copy(),
                                            cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        return contours[3]

    parser = argparse.ArgumentParser(description="Sign Testbed")
    parser.add_argument ('fileName', help='File name to process', default=['threeSigns.jpg'], nargs='*' )
    parser.add_argument ('--size', help='normalize to this size',   default='640 480' )
    parser.add_argument ('--showHSV', help='showHSV frame', default='n')
    parser.add_argument ('--showMask', help='Show mask option', default='n')
    parser.add_argument ('--pramFile', help='xmlPramaterFile', default='vidParms.xml')
    args = parser.parse_args()
    fileName = args.fileName[0]
 
    if args.showHSV == 'y':
        showHSV(fileName)

    
    cf = ColorFilter()
    cf.xmlDecodePrams ( args.pramFile )    

    if args.showMask == 'y': cf.showMask = True

    cf.addMatchTemplate ( getTemplate ( 'smallLeftTurn.png'), Runnable ('left') )
    cf.addMatchTemplate ( getTemplate ( 'smallRightTurn.png'), Runnable ('right') )
    cf.addMatchTemplate ( getTemplate ( 'smallHairpinLeft.png'), Runnable ('uTurn') )
    
    
    bgr = cv2.imread (args.fileName[0])
    bgr = cv2.resize(bgr, cf.imageSize )
    cf.parseImage( bgr ) 
    

    cv2.destroyAllWindows()


   
