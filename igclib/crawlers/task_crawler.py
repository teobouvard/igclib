from datetime import datetime

import requests
from bs4 import BeautifulSoup
import json

from igclib.constants import DEFAULT_PROVIDER, TASK_PROVIDERS, MAX_TASKS_PER_EVENT


class TaskCrawler():

    def __init__(self, provider=DEFAULT_PROVIDER, year=datetime.now().year, task_name=None):
        self.provider = TASK_PROVIDERS[provider]
        self.year = str(year)
        self.task_name = task_name

    def crawl(self):
        if self.provider['NAME'] == 'PWCA':
            return self.crawl_pwca()
        else:
            raise NotImplementedError('Provider {} not yet implemented'.format(self.provider['NAME']))
    
    def crawl_pwca(self):
        events = {}
        url = self.provider['BASE_URL'] + self.year

        year_tour = requests.get(url)
        if year_tour.status_code == 200:
            year_tour = BeautifulSoup(year_tour.text, 'lxml')
            for anchor in year_tour.find_all('a', href=True):
                if 'cup' in anchor.text.lower() and 'node' in anchor['href']:
                    event_name = anchor.string
                    events[event_name] = []
                    taskboard = anchor['href'].split('/')[-1]
                    for link in tqdm([self.provider['TASKS_URL'] + taskboard + '-' + str(x) + '.html' for x in range(MAX_TASKS_PER_EVENT)]):
                        task = requests.get(link)
                        if task.status_code == 200:
                            task = json.loads(self.provider['TASK_PATTERN'].findall(task.text)[0])
                            events[event_name].append({'task_date': task['details']['date'], 'task' : task, 'link':link})
        
        return events