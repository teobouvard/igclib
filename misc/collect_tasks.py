import requests
from bs4 import BeautifulSoup


PWCA__BASE_URL = 'http://pwca.org/'
PWCA_URL = 'http://pwca.org/view/tour/'

def generate_tour_urls():
    return [PWCA_URL + str(x) for x in range(2010, 2020)]

def fetch_events(urls):
    event_links = []

    for url in urls:
        year_tour = requests.get(url)
        if year_tour.status_code == 200:
            year_tour = BeautifulSoup(year_tour.text, 'lxml')
            for anchor in year_tour.find_all('a', href=True):
                if 'cup' in anchor.text.lower() and 'node' in anchor['href']:
                    event_links.append(PWCA__BASE_URL + anchor['href'] + '/tasks')

    return event_links

def fetch_tasks_tracks(events):
    for event in events:
        tasks = requests.get(event)
        print(tasks)

    return None, None

if __name__ == '__main__':
    urls = generate_tour_urls()
    events = fetch_events(urls)
    tasks, tracks = fetch_tasks_tracks(events)