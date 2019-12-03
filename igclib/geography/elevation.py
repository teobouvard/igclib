import json
import logging
import os

import requests

# for api key requests, contact teobouvard@gmail.com
API_KEY = os.environ.get('ELEVATION_API_KEY', '')
ELEVATION_API = f'https://geolocalisation.ffvl.fr/elevation?key={API_KEY}'


def elevation(points):
    data = [[p.lat, p.lon] for p in points]
    resp = requests.post(ELEVATION_API, data=json.dumps(data))
    if resp.status_code != 200:
        logging.warning(f'API error ({resp.status_code}) - {resp.reason} - {resp.text}')
    else:
        altitudes = json.loads(resp.text)
        return altitudes
