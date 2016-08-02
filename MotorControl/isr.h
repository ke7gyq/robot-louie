//isr.h
//C++ file to play with SWIG file

#ifndef _ISR_H
#define _ISR_H


/*
Hook 2 ISR routines. Determine quadurature distances
*/


void setup( int priority = 10 );

//For motor control
enum MDIR { OFF, FORWARD, BACKWARD, RIGHT, LEFT, TEST };
void setDir ( MDIR dir  = OFF );
// These are the output pins to the motor.
void setMPins ( int p0=17, int p1=18, int p2=27, int p3=22);


typedef void  (*CALLBACK) (void*);

struct isr {
  void * callbackArg;
  CALLBACK callback;
  int phaseA,phaseB,isrNo,  upCtr, dnCtr, distance;
  isr (int phaseA , int phaseB , int isrNo =0);  
  int getDistance(void);
  void setCallback ( CALLBACK cb, void* arg );
  double testCallback ( void );

  // Interrupt handlers.
  void _phaseA(void), _phaseB(void);


};

#endif // _ISR_H
