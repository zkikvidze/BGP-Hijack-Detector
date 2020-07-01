import requests
import json
import time
from tinydb import TinyDB, Query
import logging

logging.basicConfig(filename='status.log', format='%(asctime)s - %(message)s')

dbfile = 'database.json'

db = TinyDB(dbfile)
query = Query()

#remove previous items
db.remove(query.Type == 'net')


def getASNs():
    url = 'https://stat.ripe.net/data/country-resource-list/data.json?resource=GE'
    try:
        r = requests.get(url)
        data = r.json()
    except:
        print('function getASNS, Connection Failed.')
        logging.warning('function getASNS, Connection Failed.')
    for asn in data['data']['resources']['asn']:
        time.sleep(2)
        org = checkOrg(asn)
        prefixes = getPrefixes(asn)
        if prefixes:
            for prefix in prefixes:
                print(asn + ';' + prefix + ';' + org)
                db.insert({'Type': 'net', 'ASN': asn, 'Prefix': prefix, 'Organisation': org})
                
def getPrefixes(asn):
    url = 'https://stat.ripe.net/data/announced-prefixes/data.json?resource=' + asn
    try:
        r = requests.get(url)
        data = r.json()
    except:
        print('function getPrefixes, Connection Failed on ASN: {} Jumping to Next...'.format(asn))
        logging.warning('function getPrefixes, Connection Failed on ASN: {} Jumping to Next...'.format(asn))
        pass
    prefixes = []
    for element in data['data']['prefixes']:
        prefix = element['prefix']
        prefixes.append(prefix)
    return prefixes

def checkOrg(asn):
    url = 'https://stat.ripe.net/data/as-overview/data.json?resource=' + asn
    try:
        r = requests.get(url)
        data = r.json()
    except:
        print('function checkOrg, Connection Failed on ASN: {} Jumping to Next...'.format(asn))
        logging.warning('function getOrg, Connection Failed on ASN: {} Jumping to Next...'.format(asn))
        pass

    org = data['data']['holder']
    return org




getASNs()
