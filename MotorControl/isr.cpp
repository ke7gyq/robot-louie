/*
isr.cpp.
Play with the ISR functions.
*/

#include <wiringPi.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include "isr.h"


void setup( int priority ) {
  int myUid = geteuid();
  //printf ("UID is %d\n", myUid);
  if ( myUid ) 
    wiringPiSetupSys();
  else{
    wiringPiSetupGpio();
    piHiPri( priority  );
  }
}

int mPins[4] = { 17,18, 27,22 };
// // Set the motor pins.
// static void setMPins ( int p0,int p1, int p2, int p3){
//   // mPins[0] = p0; mPins[1] = p1; mPins[2] =p2, mPins[3] = p3;
//   pinMode( mPins[0] = p0 , OUTPUT);
//   pinMode( mPins[1] = p1 , OUTPUT);
//   pinMode( mPins[2] = p2 , OUTPUT);
//   pinMode( mPins[3] = p3 , OUTPUT);
// }

void setPins ( const int * pDir) {
  digitalWrite(mPins[0], pDir[0]);
  digitalWrite(mPins[1], pDir[1]);
  digitalWrite(mPins[2], pDir[2]);
  digitalWrite(mPins[3], pDir[3]);
}

static int dirs [2] = { 0, 0};


void setDir (MDIR dir ) {
  static const int forward[] = { 0, 1, 0 , 1 };
  static const int reverse[] = { 1, 0, 1 , 0 };
  static const int left [] = { 1,0,0,1};
  static const int right [] = { 0,1,1,0};
  static const int stop [] = {0,0,0,0};
  static const int test [] = {1,1,1,1};

  static const int leftForward [] = {0,1,0,0};
  static const int leftBackward[] = {1,0,0,0};
  static const int rightForward [] = {0,0,0,1};
  static const int rightBackward [] = {0,0,1,0};

  
  switch (dir){
  case FORWARD: setPins(forward); dirs[0]=dirs[1]=1 ;break;
  case BACKWARD:setPins(reverse); dirs[0]=dirs[1]=-1;break;
  case RIGHT: setPins(right); dirs[0]=-1; dirs[1]=1; break;
  case LEFT: setPins(left); dirs[0]=1; dirs[1]=-1 ; break;

  case RIGHTFORWARD:  setPins(rightForward); dirs[0]=1;dirs[1]=0 ;break; 
  case RIGHTBACKWARD:setPins(rightBackward); dirs[0]=-1;dirs[1]=0;break; 
  case LEFTFORWARD:  setPins(leftForward); dirs[0] =0; dirs[1]=1; break; 
  case LEFTBACKWARD: setPins(leftBackward);dirs[0] =0; dirs[1]=-1; break;

  case OFF:
  default: 
    setPins( stop); 
    dirs[0]=dirs[1] = 0;  
    break;
  }
}



static isr * rIsr[2] ;
static void int0 () {
  // printf ("Int     0\n");
  rIsr[0]->_phaseA();
}

#if(0)
static void int1 () {
  // printf ("Int     1\n");
  rIsr[0]->_phaseB();
}
#endif
static void int2 () {
  // printf ("Int2 \n");
  rIsr[1]->_phaseA();
}
#if(0)
static void int3 () {
  // printf ("Int3 \n");
  rIsr[1]->_phaseB();
}
#endif

isr::isr(int phaseA,int phaseB, int isrNo ){
  this->phaseA = phaseA;
  this->phaseB = phaseB;

  isrNo &= 1;
  this->isrNo = isrNo;
  upCtr=dnCtr=distance = 0;

  rIsr[isrNo] = this;

  pinMode ( phaseA, INPUT);
  pinMode ( phaseB, INPUT);
  // wiringPiISR( phaseA, INT_EDGE_BOTH, isrNo ? &int2 : &int0);
  // wiringPiISR( phaseB, INT_EDGE_BOTH, isrNo ? &int3 : &int1);
  wiringPiISR( phaseA, INT_EDGE_FALLING, isrNo ? &int2 : &int0);
  // wiringPiISR( phaseB, INT_EDGE_FALLING, isrNo ? &int3 : &int1);
  pullUpDnControl ( phaseA, PUD_UP);
  pullUpDnControl ( phaseB, PUD_UP);


  callbackArg = 0;
  callback = 0;
}

int isr::getDistance() {
  return distance;
}


/*
Interrupts now occur on falling edge of 
phase A

Base increment or decrement on the H bridge setting.
*/


void isr::_phaseA(void){
  int delta = dirs[isrNo];
  int s1 = digitalRead(phaseA) ? 1 : 0;
  if ( ! s1) {
    distance += delta;
    // distance += digitalRead(phaseB) ? -1:1;
    //distance += s1 == s2 ? -1 : 1 ;
  }
}


#if (0)
static void isr::_phaseA(void){
  int s1 = digitalRead(phaseA);
  if ( ! s1) {
    int s2 = digitalRead(phaseB);
    distance += s1 == s2 ? -1 : 1 ;
  }
}

// NotReached...
static void isr::_phaseB(void){
  int s2 = digitalRead(phaseB);
  if ( ! s2 ){
     int s1 = digitalRead(phaseA);
     distance += s1 == s2 ? 1 : -1;
  }
}
#endif




// Set the callback to fire when an event has completed.
void isr::setCallback (CALLBACK cb, void * arg) {
  callback = cb;
  callbackArg = arg;
}


double  isr::testCallback (){
  (*callback)( callbackArg ) ;
}

