# tokens.py.
# Run time execution of tokens.

import numpy as np
import xml.etree.ElementTree as et

#Handler for messages coming in from the outside world.
#
class MyHandler :
    def __init__(self, cf ):
        self.verbose = True
        self.cf = cf
        self.myFrame = None
        self.keywords = dict()
    
#    def addKeyword ( self, key, classHandler ):
#        self.addInstance(key, classHandler())

    def addInstance ( self, key , instance ) :
        self.keywords[key] = instance 

    def getInstance (self, key):
        try:
            instance = self.keywords[key]
            return instance
        except KeyError:
            return None

    def run ( self, inString ):
        if self.verbose:
            print "Received %s" % inString
        tokens = inString.split()
        if tokens:
            token = tokens[0]
            try :
                handler = self.keywords[token]
                s = handler.run( inString, tokens  )
                return "%s\n" %s
            except KeyError:
                 return "No Handler for keyword %s\n" % token
        else:
            return "No Tokens\n"

    
    def fromXML ( self, inFileName ):
        try :
            tree = et.parse(inFileName)
            root = tree.getroot()
        except:
            print "Tokens.py. Could not parse %s" %inFileName
            print "Using Defaults"
            return
        print "Decoded  %s " % inFileName
        if root.tag =='parms':
            for iv in root.iter ('initparam'):
                self.run ( iv.attrib['value'])






class getlow :
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        return str(self.cf.lowColor)

class gethigh:
    def __init__ ( self, cf ):
        self.cf = cf
    def run(self,inString,tokens):
        return str(self.cf.highColor)
        
class setlow:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        if len(tokens) == 4:
            try:
                self.cf.lowColor  = np.array([int(t) for t in tokens[1:]])
            except:
                pass
        return str(self.cf.lowColor)
   
class sethigh:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        if len(tokens) == 4:
            try:
                self.cf.highColor  = np.array([int(t) for t in tokens[1:]])
            except:
                pass
        return str(self.cf.highColor)
    
class getksize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        return str(cf.kernelSize)

class setksize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        try:
            self.cf.setKernel ( int(tokens[1]))
        except:
            pass
        return str(self.cf.kernelSize)

class getthreshold:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        return str (( self.cf.borderMatchThreshold, self.cf.symbolMatchThreshold))
class setthreshold:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        try:
            f1, f2  = float(tokens[1]) , float(tokens[2])
            self.cf.setMatchThreshold( f1,f2)
        except:
            pass
        return str(( self.cf.borderMatchThreshold, self.cf.symbolMatchThreshold ))
    
class getimagesize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        return str(self.cf.imageSize)

    def getValue(self):
        return self.cf.imageSize

class setimagesize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        try: 
            i1,i2 = float(tokens[1]), float(tokens[2])
            self.cf.setImageSize(i1,i2)
        except:
            pass
        return str(self.cf.imageSize)
    
class getcontourlength:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        return str(self.cf.minContourLength)

class setcontourlength:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        try: 
            i1 = float(tokens[1])
            self.cf.setMinContourLength(i1)
        except:
            pass
        return str(self.cf.minContourLength)

class verboseon:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        self.cf.verbose=True
        # myFrame.verbose=True
        return "verbose On"
        
class verboseoff:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        self.cf.verbose=False
        # myFrame.verbose=False
        return "verbose Off"

class TakePictures:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        try:
            self.cf.pString = tokens[1]
            return 'Ok'
        except:
            self.cv.pString = None
            return 'No Filename'

class Calibrate:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens):
        self.cf.doCalibrate = True
        return "Ok"
    




def getMyHandler( cf ) :
    myHandler = MyHandler (cf)
    myHandler.addInstance ( 'getlow', getlow (cf) )
    myHandler.addInstance ( 'gethigh', gethigh  (cf))
    myHandler.addInstance ( 'setlow', setlow  (cf))
    myHandler.addInstance ( 'sethigh',sethigh  (cf) )
    myHandler.addInstance ( 'getksize',getksize (cf))
    myHandler.addInstance ( 'setksize',setksize (cf))
    myHandler.addInstance ( 'getthreshold',getthreshold(cf))
    myHandler.addInstance ( 'setthreshold',setthreshold(cf))
    myHandler.addInstance ( 'getimagesize',getimagesize(cf))
    myHandler.addInstance ( 'setimagesize',setimagesize(cf))
    myHandler.addInstance ( 'getcontourlength',getcontourlength(cf))
    myHandler.addInstance ( 'setcontourlength',setcontourlength(cf))
    myHandler.addInstance ( 'verboseon',verboseon(cf))
    myHandler.addInstance ( 'verboseoff',verboseoff(cf))
    myHandler.addInstance ( 'takepictures', TakePictures(cf))
    myHandler.addInstance ( 'calibrate', Calibrate(cf))
    return myHandler


