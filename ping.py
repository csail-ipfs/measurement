import requests, jsonlines, platform
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import os.path

API = "http://localhost:5001/api/v0/ping"
VP = platform.node()
STORAGE = os.path.join(str(Path.home()), "dht-data")

config = {
	'username': '',
	'password': '',
	'ip': '',
	'database': ''
}
if not config['ip']: raise ValueError("Please update the `config` variable before running.")

def pingMyOldPeers(daysAgo):
	"""Get ping results for all known peers seen at `daysAgo` days."""
	
	peers = getOldKPs(VP, daysAgo)

	# In case something goes wrong...
	if not peers['Peers']: 
		print("No observations found, exiting.")
		return False

	# First dump the query results to disk
	print("Obtaining peers from {d} days ago on {vp}...".format(d=daysAgo, vp=VP))
	with open(os.path.join(STORAGE, "ping.{vp}.time.config".format(vp=VP, time=daysAgo*86400)), 'w') as f:
		json.dump(peers, f)	

	# Then iterate through the list, and append results of ping
	for addr in tqdm(peers['Peers']):
		with open(os.path.join(STORAGE, "ping.{vp}.{time}".format(vp=VP, time=daysAgo*86400)), "a") as out:
			try:
				result = json.dumps(ping(addr))
				out.write( result + "\n" )
			except:
				print("Skipping ", addr)
				with open("/tmp/ping.error.log", "a") as eout:
					eout.write(addr)

def pingSubsetList(fn="peersubset.txt"):
	"""Ping all the addresses found in a newline delimited file."""
	
	with open(fn) as f:
		peers = f.readlines()

	for peer in tqdm(peers):
		with open(os.path.join(STORAGE, "ping.{host}".format(host=VP)), "a") as out:
			try:
				result = json.dumps(ping(peer))
				out.write( result + "\n" )
			except:
				print("Skipping ", peer)
				with open("/tmp/ping.error.log", "a") as eout:
					eout.write(peer)


def getOldKPs(vantage, daysAgo):
	"""Get set of known peers from logs from `daysAgo` days in the past for `vantage`. """
	
	client = MongoClient("mongodb://{username}:{password}@{ip}/{database}".format(**config))
	db = client['ipfs']
	
	seconds = daysAgo * 86400
	now = int(datetime.now().strftime("%s"))
	window = 60 * 5 # 5 minutes in seconds
	
	query = {
		'VANTAGE': vantage, 
		'TIMESTAMP': {'$gte': now - seconds - window, '$lte': now - seconds + window }
	}

	result = db.knownpeers.find(query)
	seenPeers = set()
	times = []
	for observation in result:
		seenPeers.update( set(observation['Addrs'].keys()) )
		times.append(observation['TIMESTAMP'])
	return { 
		'Peers': list(seenPeers),
		'VANTAGE': vantage,		
		'TIMESTAMP_RANGE': times,
		'NOW': now,
		'DAYSAGO': daysAgo
	}


def ping(addr,timeout=6):
	addr = addr.strip()
	params = {
		'count': 5,
		'arg': addr
	}
	result = {
		'TIMESTAMP': datetime.now().strftime("%s"),
		'VANTAGE': VP,
		'Success': None,
		'Times': [],
		'Error': '',
		'Address': addr
	}
	try:
		response = requests.get(API, params=params, timeout=timeout)
	except:
		result['Success'] = False
		result['Error'] = 'TIMEOUT'
		return result

	output = list(jsonlines.Reader(response.text.split("\n")[0:-1]))
	
	if len(output) == 1:
		# Something went wrong
		result['Success'] = False
		result['Error'] = 'NXPEER'
		return result
			
	elif len(output) == 2:
		assert output[0]['Success'] == True
		assert output[1]['Success'] == False
		result['Success'] = False
		result['Error'] = output[1]['Text']
		return result

	elif len(output) >= 3:
		assert output[0]['Success'] == True
		if output[-1]['Success'] == True and output[-1]['Text']:		
			times = [line['Time'] for line in output[1:-1]]
			result['Times'] = times
			result['Success'] = True
			return result
		else:
			result['Error'] = output[-1]['Text']
			return result
	else:
		raise Exception("IPFS API did not return valid value.")
		
if __name__ == '__main__':
	import sys, json
	from tqdm import tqdm
	
	pingTimes = [1.0/24, 1, 7]
	for age in pingTimes: pingMyOldPeers(age)

	