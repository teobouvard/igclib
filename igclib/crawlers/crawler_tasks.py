import json
import re
import pickle
import os

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

PWCA__TASKS_URL = 'http://pwca.org/sites/default/files/taskboards/pwctb'
PWCA_URL = 'http://pwca.org/view/tour/'
TASK_PATTERN = re.compile('xctask.map.taskjsn = (.*?);')
TASK_DIR = 'data/tasks'


def generate_tour_urls():
    return [PWCA_URL + str(x) for x in range(2010, 2020)]


def fetch_events(urls):
    event_links = []

    for url in tqdm(urls, desc='Fetching events'):
        year_tour = requests.get(url)
        if year_tour.status_code == 200:
            year_tour = BeautifulSoup(year_tour.text, 'lxml')
            for anchor in year_tour.find_all('a', href=True):
                if 'cup' in anchor.text.lower() and 'node' in anchor['href']:
                    taskboard = anchor['href'].split('/')[-1]
                    event_links.extend([PWCA__TASKS_URL + taskboard + '-' + str(x) + '.html' for x in range(11)])

    return event_links


def fetch_tasks(events):
    tasks = []

    for event in tqdm(events, desc='Fetching tasks'):
        task = requests.get(event)
        if task.status_code == 200:
            task = TASK_PATTERN.findall(task.text)[0]
            tasks.append(json.loads(task))

    return tasks


def save_tasks(tasks):
    os.makedirs(TASK_DIR, exist_ok=True)
    for task in tasks:
        with open(os.path.join(TASK_DIR, task['details']['date'] + '.json'), 'w') as f:
            json.dump(task, f)


if __name__ == '__main__':
    urls = generate_tour_urls()
    events = fetch_events(urls)
    tasks = fetch_tasks(events)
    save_tasks(tasks)
