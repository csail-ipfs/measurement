import csv, requests
import json
from tqdm import tqdm


def scrape(hashlist, output, timeout=30):
    """Attempt to scrape info about all hashes in file `hashlist`."""
    API = "http://127.0.0.1:5001/api/v0/object/stat?arg={0}&encoding=json"

    with open(hashlist) as f:
        hashes = list(csv.reader(f))

    results = []
    timeouts = []

    # Grab object info from the API
    for _, h in tqdm(hashes):
        try:
            result = requests.get(
                API.format(h), timeout=timeout
            )
            results.append(result.json())
        except:
            timeouts.append(h)

    return results, timeouts


if __name__ == '__main__':
    HASH_LIST = sys.argv[1]
    TIMEOUT = sys.argv[2]
    OUTPUT = sys.argv[3]

    if len(sys.argv) != 4:
        print(
            "Usage: python3 {0} <hashlist.txt> <timeout> <output.json>".format(
                sys.argv[0]
            )
        )

    results, timeouts = scrape(HASH_LIST, OUTPUT, TIMEOUT)
    with open(OUTPUT, 'w') as f:
        json.dump(
            {'timeouts': timeouts, 'results': results}, f
        )
