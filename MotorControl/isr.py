# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_isr', [dirname(__file__)])
        except ImportError:
            import _isr
            return _isr
        if fp is not None:
            try:
                _mod = imp.load_module('_isr', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _isr = swig_import_helper()
    del swig_import_helper
else:
    import _isr
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0



def setup(priority=10):
  return _isr.setup(priority)
setup = _isr.setup
OFF = _isr.OFF
FORWARD = _isr.FORWARD
BACKWARD = _isr.BACKWARD
RIGHT = _isr.RIGHT
LEFT = _isr.LEFT
TEST = _isr.TEST
RIGHTFORWARD = _isr.RIGHTFORWARD
RIGHTBACKWARD = _isr.RIGHTBACKWARD
LEFTFORWARD = _isr.LEFTFORWARD
LEFTBACKWARD = _isr.LEFTBACKWARD

def setDir(*args):
  return _isr.setDir(*args)
setDir = _isr.setDir

def setMPins(p0=17, p1=18, p2=27, p3=22):
  return _isr.setMPins(p0, p1, p2, p3)
setMPins = _isr.setMPins
class isr(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, isr, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, isr, name)
    __repr__ = _swig_repr
    __swig_setmethods__["callbackArg"] = _isr.isr_callbackArg_set
    __swig_getmethods__["callbackArg"] = _isr.isr_callbackArg_get
    if _newclass:callbackArg = _swig_property(_isr.isr_callbackArg_get, _isr.isr_callbackArg_set)
    __swig_setmethods__["callback"] = _isr.isr_callback_set
    __swig_getmethods__["callback"] = _isr.isr_callback_get
    if _newclass:callback = _swig_property(_isr.isr_callback_get, _isr.isr_callback_set)
    __swig_setmethods__["phaseA"] = _isr.isr_phaseA_set
    __swig_getmethods__["phaseA"] = _isr.isr_phaseA_get
    if _newclass:phaseA = _swig_property(_isr.isr_phaseA_get, _isr.isr_phaseA_set)
    __swig_setmethods__["phaseB"] = _isr.isr_phaseB_set
    __swig_getmethods__["phaseB"] = _isr.isr_phaseB_get
    if _newclass:phaseB = _swig_property(_isr.isr_phaseB_get, _isr.isr_phaseB_set)
    __swig_setmethods__["isrNo"] = _isr.isr_isrNo_set
    __swig_getmethods__["isrNo"] = _isr.isr_isrNo_get
    if _newclass:isrNo = _swig_property(_isr.isr_isrNo_get, _isr.isr_isrNo_set)
    __swig_setmethods__["upCtr"] = _isr.isr_upCtr_set
    __swig_getmethods__["upCtr"] = _isr.isr_upCtr_get
    if _newclass:upCtr = _swig_property(_isr.isr_upCtr_get, _isr.isr_upCtr_set)
    __swig_setmethods__["dnCtr"] = _isr.isr_dnCtr_set
    __swig_getmethods__["dnCtr"] = _isr.isr_dnCtr_get
    if _newclass:dnCtr = _swig_property(_isr.isr_dnCtr_get, _isr.isr_dnCtr_set)
    __swig_setmethods__["distance"] = _isr.isr_distance_set
    __swig_getmethods__["distance"] = _isr.isr_distance_get
    if _newclass:distance = _swig_property(_isr.isr_distance_get, _isr.isr_distance_set)
    def __init__(self, *args): 
        this = _isr.new_isr(*args)
        try: self.this.append(this)
        except: self.this = this
    def getDistance(self): return _isr.isr_getDistance(self)
    def testCallback(self): return _isr.isr_testCallback(self)
    def _phaseA(self): return _isr.isr__phaseA(self)
    def _phaseB(self, *args): return _isr.isr__phaseB(self, *args)
    def setCallback(self, *args): return _isr.isr_setCallback(self, *args)
    __swig_destroy__ = _isr.delete_isr
    __del__ = lambda self : None;
isr_swigregister = _isr.isr_swigregister
isr_swigregister(isr)

# This file is compatible with both classic and new-style classes.


