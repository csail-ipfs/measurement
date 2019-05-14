#!/bin/bash

if pgrep -x "ipfs" > /dev/null
then
	echo "IPFS is already running"
else
	echo "Starting IPFS daemon in screen"
	screen -S ipfs -d -m ipfs daemon

	echo "Waiting 10 seconds..."
	sleep 10
	
	echo "Starting logging process"
	screen -S logging -d -m /usr/bin/watch -c -d -n 120 $HOME/measurement/makelogs.sh

	echo "Starting DHT logging process"
	screen -S dht -d -m $HOME/measurement/makedht.sh
	
	screen -list
fi

