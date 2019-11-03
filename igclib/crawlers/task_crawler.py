import asyncio
import json
import sys
from datetime import datetime

import aiohttp
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from igclib.constants import (DEFAULT_PROVIDER, MAX_TASKS_PER_EVENT,
                              TASK_PROVIDERS)


class TaskCrawler():

    def __init__(self, provider=DEFAULT_PROVIDER, year=datetime.now().year, progress='gui'):
        self._progress = progress
        self.provider = TASK_PROVIDERS[provider]
        self.year = str(year)


    def crawl(self):
        if self.provider['NAME'] == 'PWCA':
            return self.crawl_pwca()
        else:
            raise NotImplementedError(f'Provider {self.provider["NAME"]} not yet implemented')


    def crawl_pwca(self):
        url = self.provider['BASE_URL'] + self.year
        links = self.fetch_pwca_links(url)
        loop = asyncio.get_event_loop()
        events = loop.run_until_complete(self.download_list(links))
        loop.close()
        return events
    

    def fetch_pwca_links(self, url):
        links = {}

        year_tour = requests.get(url)
        if year_tour.status_code == 200:
            year_tour = BeautifulSoup(year_tour.text, 'lxml')
            for anchor in year_tour.find_all('a', href=True):
                if 'cup' in anchor.text.lower() and 'node' in anchor['href']:
                    event_name = anchor.string
                    taskboard = anchor['href'].split('/')[-1]
                    for link in [self.provider['TASKS_URL'] + taskboard + '-' + str(x) + '.html' for x in range(MAX_TASKS_PER_EVENT)]:
                        if event_name in links:
                            links[event_name].append(link)
                        else:
                            links[event_name] = [link]
        
        return links
    
    async def download_list(self, links):
        events = {}
        steps = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as client:
            for event_name, links in links.items():
                for link in links:
                    step = asyncio.ensure_future(self.fetch(client, event_name, link))
                    steps.append(step)

            responses = []
            for r in tqdm(asyncio.as_completed(steps), total=len(steps), disable=self._progress!='gui'):
                response = await r
                responses.append(response)
                if self._progress == 'ratio':
                    print(f'{len(responses)}/{len(steps)}', file=sys.stderr, flush=True)

            responses = [r for r in responses if r is not None]

            for response in responses:
                event_name = response['event_name']
                task = response['task']
                link = response['link']
                if event_name in events:
                    events[event_name].append({'task_date': task['details']['date'], 'task': task, 'link': link})
                else:
                    events[event_name] = [{'task_date': task['details']['date'], 'task': task, 'link':link}]

            return events
    
    async def fetch(self, client, event_name, link):
        async with client.get(link) as r:
            if r.status == 200:
                response = await r.text()
                return dict(event_name=event_name, task=json.loads(self.provider['TASK_PATTERN'].findall(response)[0]), link=link)


if __name__ == '__main__':
    from igclib.crawlers.task_crawler import TaskCrawler
    tc = TaskCrawler()
    tc.crawl()
