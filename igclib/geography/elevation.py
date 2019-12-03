import json
import requests
import logging
import os

# for api key requests, contact dGVvYm91dmFyZEBnbWFpbC5jb20K (base64)
API_KEY = os.environ.get('ELEVATION_API_KEY', '')
ELEVATION_API = f'https://geolocalisation.ffvl.fr/elevation?key={API_KEY}'

def elevation(points):
    data = [[p.lat, p.lon] for p in points]
    resp = requests.post(ELEVATION_API, data=json.dumps(data))
    if resp.status_code != 200:
        logging.warning(f'API error ({resp.status_code}) - {resp.reason}')
    else:
        altitudes = json.loads(resp.text)
        return altitudes
