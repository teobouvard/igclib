import asyncio
import json
import sys
from datetime import datetime

import aiohttp
import requests
from bs4 import BeautifulSoup
from igclib.constants import (DEFAULT_PROVIDER, MAX_TASKS_PER_EVENT, TASK_PROVIDERS)
from tqdm import tqdm
from igclib.core.base import BaseObject


class TaskCrawler(BaseObject):

    def __init__(self, provider=DEFAULT_PROVIDER, year=datetime.now().year, progress='gui'):
        self._progress = progress
        self.provider = TASK_PROVIDERS[provider]
        self.year = str(year)
        self.crawl()

    def crawl(self, output=None):
        if self.provider['NAME'] == 'PWCA':
            self.tasks = self.crawl_pwca()
        else:
            raise NotImplementedError(f'Provider {self.provider["NAME"]} not yet implemented')

    def serialize(self):
        return self.tasks

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
        else:
            raise ValueError('PWCA did not respond')

        return links

    async def download_list(self, links):
        steps = []
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as client:
            for event_name, links in links.items():
                for link in links:
                    step = asyncio.ensure_future(self.fetch(client, event_name, link))
                    steps.append(step)

            responses = []
            for r in tqdm(asyncio.as_completed(steps), total=len(steps), disable=self._progress != 'gui'):
                response = await r
                responses.append(response)
                if self._progress == 'ratio':
                    print(f'{len(responses)/len(steps):.0%}', file=sys.stderr, flush=True)

            responses = [r for r in responses if r is not None]

            events = {}
            for response in responses:
                event_name = response['event_name']
                provider = self.provider
                year = self.year
                task_num = response['task']['details']['task']
                task = response['task']
                if event_name in events:
                    events[event_name]['tasks'].append({'num': task_num, 'task': task})
                else:
                    events[event_name] = {'event': event_name, 'provider': self.provider['NAME'], 'year': self.year, 'tasks': []}
                    events[event_name]['tasks'].append({'num': task_num, 'task': task})

            for event in events.values():
                event['tasks'].sort(key=lambda x: x['num'])

            return list(events.values())

    async def fetch(self, client, event_name, link):
        async with client.get(link) as r:
            if r.status == 200:
                response = await r.text()
                return dict(event_name=event_name, task=json.loads(self.provider['TASK_PATTERN'].findall(response)[0]))


if __name__ == '__main__':
    from igclib.crawlers.task_crawler import TaskCrawler
    tc = TaskCrawler()
    tc.crawl()
