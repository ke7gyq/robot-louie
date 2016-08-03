#!/bin/bash
# setGpio.sh 
# Enable outputs for GPIO on the tracks.


gpio mode 0 out
gpio mode 1 out
gpio mode 2 out
gpio mode 3 out


#gpio export 0 out
#gpio export 1 out
#gpio export 2 out
#gpio export 3 out

gpio export 17 out
gpio export 18 out
gpio export 27 out
gpio export 22 out


gpio mode 4 in
gpio mode 5 in
gpio mode 6 in
gpio mode 7 in



cmd=${1-"stop"}

echo "Cmd is $cmd"

# Forward.
if [ $cmd == "forward" ] ; then
	gpio write 0 0 
	gpio write 1 1
	gpio write 2 0
	gpio write 3 1 
elif [ $cmd = "reverse" ] ; then
	gpio write 0 1 
	gpio write 1 0
	gpio write 2 1
	gpio write 3 0 
elif [ $cmd = "stop" ] ; then
	gpio write 0 0 
	gpio write 1 0
	gpio write 2 0
	gpio write 3 0 
elif [ $cmd = "left" ] ; then
	gpio write 0 1 
	gpio write 1 0
	gpio write 2 0
	gpio write 3 1 
elif [ $cmd = "right" ] ; then
	gpio write 0 0 
	gpio write 1 1
	gpio write 2 1
	gpio write 3 0 
else
	gpio write 0 0
	gpio write 1 0
	gpio write 2 0
	gpio write 3 0
fi




