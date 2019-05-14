Measurement scripts for logging IPFS system state.

# Architecture

* Data ingestion (all metrics): MongoDB server on OpenStack
* Data ingestion (DHT): Google Cloud NFS Filestore with flat file logs
* Vantage points: Debian VMs (10GB disk/3GB RAM) on Google Compute Engine based on a standardized image which has the following packages:
	* jq - JSON stream processor
	* mongodb-clients - For sending logs to server
	* golang-1.12/unstable - For IPFS
	* ipfs-update, ipfs - IPFS daemon
	* nfs-common - For mounting DHT datastore

# Data structure

Ingestion is into five Mongo collections and done every 120 seconds:

* ipfsconfig: one document per vantage point with a dump of the IPFS configuration
* bandwidth: 
	* LOGTYPE key is either `bw` or `bw_all`
	* `bw_all`: IPFS internal cumulative bandwidth
	* `bw`: see the `NOTE` key for the specific protocol whose bandwidth is being measured
* bitswap
* knownpeers
* openpeers

Due to IPFS logging API limitations, DHT data is written to a flat file on the NFS server, mounted at `$HOME/dht-data` on each VM. Each log will be post processed and streamed into MongoDB after collection is done, instead of in real time.

# Logging scripts

* `autorun-provision-node` should be run once when standing up a new VM. It will automatically install all necessary software and pull down scripts from this Git repository.
	* A flag file is created at `$HOME/.ipfs-probe-provision-complete` after initial set up. If the script is run again, it will just start the logging process (`measure.sh`) instead. 
	* This allows the script to be safely autorun by GCE upon every (re)start of a VM, allowing for complete automation.
* `makedht.sh` streams output from the IPFS logging system through `jq` to discard any non-DHT logging keys, and writes to the NFS volume.
* `makelogs.sh` queries the IPFS logging APIs for **bandwidth, bitswap, openpeers, knownpeers** and sends the emitted JSON to the MongoDB server.
* `measure.sh` automatically starts the IPFS daemon and the other two logging scripts in screen sessions.

## Monitoring tools

* `gcloud-provision` uses the Google Cloud API to automatically start another instance in a specified zone, preconfigured
* `get-status.py` gives basic metrics for the current number of observations on the MongoDB server.