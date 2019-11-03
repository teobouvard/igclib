import requests
import zipfile
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys

from igclib.constants import FLIGHT_PROVIDERS

class FlightCrawler():

    def __init__(self, task, progress=None):
        self._progress = progress
        self.crawl_pwca(task)
        self.directory = f'/tmp/{task.date}'

    def crawl_pwca(self, task):
        date = datetime.strptime(task.date, '%Y-%m-%d')
        tag = re.compile(f'T.*{datetime.strftime(date, "%a %d %b %y")}')

        results_page = 'results/' if datetime.now().year == date.year else f'results_{date.year}/'
        URL = FLIGHT_PROVIDERS['PWCA']['BASE_URL'] + results_page
        
        page = requests.get(URL + 'results.htm')
        event = BeautifulSoup(page.text, 'lxml').find('b', string=tag)
        tracks_link = event.find_next_sibling('a').attrs.get('href', None)

        tracks = requests.get(URL + tracks_link, stream=True)
        file_size = int(tracks.headers.get('content-length', 0))

        with open(f'/tmp/{task.date}.zip', 'wb') as f:
            downloaded = 0
            with tqdm(total=file_size, desc='downloading_tracks', disable=self._progress!='gui') as pbar: 
                for data in tracks.iter_content(32*1024): 
                    f.write(data); 
                    if self._progress == 'ratio':
                        downloaded += len(data)
                        print(f'{downloaded}/{file_size}', file=sys.stderr, flush=True)
                    else:
                        pbar.update(len(data))

        z = zipfile.ZipFile(f'/tmp/{task.date}.zip')
        z.extractall(f'/tmp/{task.date}')
        os.remove(f'/tmp/{task.date}.zip')
