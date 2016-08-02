/* isr.i
Play with python bindings.
*/

%module isr

%{
#include "isr.h"
%}



// Grab a Python function object as a Python object.
// %typemap(python,in) PyObject *pyfunc {

#if defined(SWIGPYTHON)
%typemap(in) PyObject *pyfunc {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
      return NULL;
  }
  $1=$input;
}
#endif


%{
static void PythonCallBack( void *clientdata){
  PyObject *func, *arglist;
  PyObject *result;
  double    dres = 0;
  
  func = (PyObject *) clientdata;               // Get Python function
  arglist = Py_BuildValue("()");             // Build argument list
  result = PyEval_CallObject(func,arglist);     // Call Python
  Py_DECREF(arglist);                           // Trash arglist
  Py_XDECREF(result);
}
%}


%include "isr.h"


// Attach a new method to our plot widget for adding Python functions
%extend isr {
   // Set a Python function object as a callback function
   // Note : PyObject *pyfunc is remapped with a typempap
   void setCallback(PyObject *pyfunc) {
     self->setCallback(PythonCallBack, (void *) pyfunc);
     Py_INCREF(pyfunc);
   }
}

