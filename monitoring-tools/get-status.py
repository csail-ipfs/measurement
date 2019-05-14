from pymongo import MongoClient
import itertools
from collections import defaultdict
from tqdm import tqdm

config = {
	'username': '',
	'password': '',
	'ip': '',
	'database': ''
}

if not config['ip']: raise ValueError("Please edit the `config` variable.")

client = MongoClient("mongodb://{username}:{password}@{ip}/{database}".format(**config))
db = client[config['database']]

print("Total vantage points: %s" % db.ipfsconfig.count_documents({}))
print("\n".join("* {host}".format(host=host) for host in db.bandwidth.distinct('VANTAGE')))

print("Bandwidth observations: %s" % db.bandwidth.count({}))
print("Known peer observations: %s" % db.knownpeers.count({}))
print("Open peer observations: %s" % db.openpeers.count({}))
print("Bitswap observations: %s" % db.bitswap.count({}))

print("Calculating unique peers seen...")

query = db.knownpeers.aggregate([
		{"$match": {'VANTAGE': 'ipfs-big'}},						# Query all documents
		
		{"$project":
			{
				"arrayofkeyvalue": {"$objectToArray":"$Addrs"}, 	# doc.Addrs.values
				"VANTAGE": "$VANTAGE"								# Carry over VP info
			},
		},
		{"$project":
			{
				"keys":"$arrayofkeyvalue.k", 						# Turn into array
				"VANTAGE": "$VANTAGE"								# Carry over VP info
			}
		}
])

result = defaultdict(set)
for page in tqdm( query ):
	v = page['VANTAGE']
	peers = page['keys']
	result[v].update( peers )

unique_all = set( itertools.chain.from_iterable(result.values()) )

print("%s unique peers seen across all vantage points" % len(unique_all))
for vantage, peers in result.items():
	print("\t * {v}: {n}".format(v=vantage, n=len(peers)))