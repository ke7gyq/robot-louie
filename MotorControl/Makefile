# Makefile for isr.

PYINC=/usr/include/python2.7


all:_isr.so

_isr.so:isr.o isr_wrap.o
	g++ -shared isr.o isr_wrap.o -l wiringPi -o _isr.so

isr.o:isr.cpp
	g++ -O2 -fPIC -c  isr.cpp

isr_wrap.o:isr_wrap.cxx
	g++ -O2 -fPIC -c  -I$(PYINC) isr_wrap.cxx

isr_wrap.cxx:isr.i isr.h
	swig -c++ -python isr.i


clean:
	rm -f *.o *.so isr_wrap.cxx isr.py isr.pyc *~
