#!/bin/bash

# Due to how the data is streamed from the IPFS client we can't chain multiple jq operators
# like in the other script. 
echo "Starting DHT logging process at $(date)"
curl -s --no-buffer http://localhost:5001/api/v0/log/tail | jq --unbuffered --arg host $(hostname) -c 'select( .Tags.system == "dht" ) + {LOGTYPE: "dht", VANTAGE: $host}' >> $HOME/dht-data/dht.$(hostname).log