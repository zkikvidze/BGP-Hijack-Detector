import requests
import json
import csv
from tinydb import TinyDB, Query
import logging

logging.basicConfig(filename='status.log', format='%(asctime)s - %(message)s')


db = TinyDB('database.json')
query = Query()



def checkPath(path_asn, asn, prefix, org, source_owner, source_asn):
    asn = str(asn)
    path_asn = str(path_asn)
    source_asn = str(source_asn)
    url = 'https://stat.ripe.net/data/rir/data.json?resource=' + path_asn + '&lod=2'
    try:
        r = requests.get(url)
        data = r.json()
    except:
        print('function checkPath, Connection Failed on Path-ASN: {} Jumping to Next...'.format(path_asn))
        logging.warning('function checkPath, Connection Failed on Path-ASN: {} Jumping to Next...'.format(path_asn))
    try:
        for country in data['data']['rirs']:
            country = country['country']
            if country == 'RU':
                print('ALERT!!! GRUTUNI DETECTED ' + asn + ',' + prefix + ',' + org + ' From: ' + source_owner + ',' + source_asn + ' GRUTUN ASN: ' + path_asn)
                logging.warning('ALERT!!! GRUTUNI DETECTED ' + asn + ',' + prefix + ',' + org + ' From: ' + source_owner + ',' + source_asn + ' GRUTUN ASN: ' + path_asn)
                db.insert({'Type': 'alert', 'ASN': asn, 'Prefix': prefix, 'Organisation': org, 'Path_ASN': path_asn, 'Source_asn:': source_asn, 'Source_owner': source_owner})
            else:
                print(path_asn + ',' + country)
    except:
        print('Cant pull information about ' + path_asn + ' skipping..')
        logging.warning('Cant pull information about ' + path_asn + ' skipping..')
        
def getPath(prefix, asn, org):
    url = 'https://stat.ripe.net/data/bgplay/data.json?resource=' + prefix + '&rrcs=0'
    r = requests.get(url)
    data = r.json()
    try:
        source_owner = data['data']['nodes'][0]['owner']
        source_asn = data['data']['nodes'][0]['as_number']
        print('Testing path from ' + source_owner + ',' + str(source_asn))
        for path_asn in data['data']['initial_state'][0]['path']:
            path_result = {'path_asn': path_asn, 'source_owner': source_owner, 'source_asn': source_asn}
            checkPath(path_asn, asn, prefix, org, source_owner, source_asn)
    except:
        print(prefix + ' is not allocated. Will skip...')

#remove previuos items
db.remove(query.Type == 'alert')

for item in db.all():
    if item['Type'] == 'net':
        asn = item['ASN']
        prefix = item['Prefix']
        org = item['Organisation']
        print('starting to check Network: ASN: ' + asn + ' Prefix: ' + prefix + ' Organisation: ' + org)
        getPath(prefix, asn, org)  
