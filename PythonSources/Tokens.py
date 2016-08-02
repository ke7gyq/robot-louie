# tokens.py.
# Run time execution of tokens.

import numpy as np

#Handler for messages coming in from the outside world.
#
class MyHandler :
    def __init__(self, cf ):
        self.verbose = True
        self.cf = cf
        self.myFrame = None
        self.keywords = dict()
    
    def addKeyword ( self, key, classHandler ):
        self.addInstance(key, classHandler())
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
                s = handler.run( inString, tokens, self.cf, self.myFrame )
                return "%s\n" %s
            except KeyError:
                 return "No Handler for keyword %s\n" % token
        else:
            return "No Tokens\n"


class getlow :
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        return str(cf.lowColor)

class gethigh:
    def __init__ ( self, cf ):
        self.cf = cf
    def run(self,inString,tokens, cf, myFrame):
        return str(cf.highColor)
        
class setlow:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        if len(tokens) == 4:
            try:
                cf.lowColor  = np.array([int(t) for t in tokens[1:]])
            except:
                pass
        return str(cf.lowColor)
   

 

class sethigh:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        if len(tokens) == 4:
            try:
                cf.highColor  = np.array([int(t) for t in tokens[1:]])
            except:
                pass
        return str(cf.highColor)
    
class getksize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        return str(cf.kernelSize)

class setksize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        try:
            cf.setKernel ( int(tokens[1]))
        except:
            pass
        return str(cf.kernelSize)

class getthreshold:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        return str (( cf.borderMatchThreshold, cf.symbolMatchThreshold))
class setthreshold:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        try:
            f1, f2  = float(tokens[1]) , float(tokens[2])
            cf.setMatchThreshold( f1,f2)
        except:
            pass
        return str(( cf.borderMatchThreshold, cf.symbolMatchThreshold ))
    
class getimagesize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        return str(self.cf.imageSize)

    def getValue(self):
        return self.cf.imageSize

class setimagesize:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        try: 
            i1,i2 = float(tokens[1]), float(tokens[2])
            cf.setImageSize(i1,i2)
        except:
            pass
        return str(cf.imageSize)
    
class getcontourlength:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        return str(cf.minContourLength)

class setcontourlength:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        try: 
            i1 = float(tokens[1])
            cf.setMinContourLength(i1)
        except:
            pass
        return str(cf.minContourLength)

class verboseon:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        cf.verbose=True
        myFrame.verbose=True
        return "verbose On"
        
class verboseoff:
    def __init__ ( self, cf ):
        self.cf = cf
    def run( self,inString, tokens, cf, myFrame):
        cf.verbose=False
        myFrame.verbose=False
        return "verbose Off"



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

    return myHandler


