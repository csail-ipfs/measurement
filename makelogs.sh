#!/bin/bash
source $HOME/measurement/json_helpers
source $HOME/measurement/mongo_helpers
############################## Configuration ##################################

############################## API endpoints ##################################

# API endpoints for IPFS logging
ENDPOINT="localhost:5001/api/v0"
API_BW="/stats/bw"
API_BIT="/stats/bitswap"
API_PEERS="/swarm/peers"
API_KNOWN="/swarm/addrs"

############################## API arguments ##################################

# Arguments for bandwidth stats
# See https://github.com/libp2p/specs/blob/master/7-properties.md#757-protocol-multicodecs
IPFS_PROTOS="/secio/1.0.0 /plaintext/1.0.0 /spdy/3.1.0 /yamux/1.0.0 /mplex/6.7.0 /ipfs/id/1.0.0 /ipfs/ping/1.0.0 /libp2p/relay/circuit/0.1.0 /ipfs/diag/net/1.0.0 /ipfs/kad/1.0.0 /ipfs/bitswap/1.0.0"

############################### Log outputs ###################################

# Temporary output files
FILE_BW="bandwidth.log"
FILE_BIT="bitswap.log"
FILE_PEERS="open.peers.log"
FILE_KNOWN="known.peers.log"

###############################################################################

echo -ne "Measuring at $(date +%s)... "
echo

# Update each log

# Bandwidth (all)
fetchAPI $API_BW "proto=" | annotate_type "bw_all" | timestamp >> $FILE_BW

# Bandwidth (by proto)
for proto in $IPFS_PROTOS; do
	fetchAPI $API_BW "proto=$proto" | annotate $proto | annotate_type "bw_proto" | timestamp >> $FILE_BW
done

# Bitswap
fetchAPI $API_BIT | annotate_type "bitswap" | timestamp >> $FILE_BIT

# Peers
fetchAPI $API_PEERS | annotate_type "openpeers" | timestamp >> $FILE_PEERS

# Known addresses
fetchAPI $API_KNOWN | annotate_type "knownpeers"  | timestamp >> $FILE_KNOWN

echo -ne "Updating database... "
mimport --collection bandwidth --file $FILE_BW
mimport --collection bitswap --file $FILE_BIT
mimport --collection knownpeers --file $FILE_KNOWN
mimport --collection openpeers --file $FILE_PEERS

echo -ne "Cleaning up temporary files..."
rm $FILE_BW $FILE_BIT $FILE_KNOWN $FILE_PEERS

echo -ne "Finished at $(date) %\033[0K\r"
echo
