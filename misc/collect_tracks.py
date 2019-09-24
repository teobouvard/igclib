import os
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

DATA_FOLDER = '../data/tracks/'
PWCA_URL = 'http://pwca.org/results/results'

def generate_urls():
    urls = [''.join([PWCA_URL, '_', str(x), '/results.htm']) for x in range(2010, 2020)]
    urls.append(PWCA_URL + '/results.htm')
    return urls

def generate_igc_links(url_list):
    files = []

    for url in url_list:
        index = requests.get(url)
        if index.status_code != 200:
            print('{} not found'.format(url))
        else:
            html = BeautifulSoup(index.text, 'lxml')
            for anchor in html.find_all('a', href=True):
                if anchor.text == 'IGC':
                    basename = url.rsplit('/', 1)[0]
                    link = anchor['href']
                    files.append('/'.join([basename, link]))

    return files

def download_igc(links):
    for link in tqdm(links):
        filename = link.split('/')[-1]
        subdir = link.split('/')[-2]
        filename = os.path.join(DATA_FOLDER, subdir, filename)

        if os.path.exists(filename):
            continue

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'wb') as f:
            downloaded_file = requests.get(link)
            f.write(downloaded_file.content)

def unzip_files(folder):
    for root, _, files in os.walk(folder):
        for filename in files:
            if filename.endswith('.zip'):
                with zipfile.ZipFile(os.path.join(root, filename), 'r') as f:
                    try:
                        f.extractall(path=os.path.join(root, filename.split('.')[0]))
                    except zipfile.BadZipFile as e:
                        print(e)

                    os.remove(os.path.join(root, filename))

def clean_data(folder):
    for root, dirs, files in os.walk(folder):

        if len(dirs) == 1 and len(files) == 0:
            file_list = os.listdir(os.path.join(root,dirs[0]))
            for f in file_list:
                shutil.move(os.path.join(root, dirs[0], f), root)
            os.removedirs(os.path.join(root, dirs[0]))

if __name__ == '__main__':

    urls = generate_urls()
    links = generate_igc_links(urls)
    download_igc(links)
    unzip_files(DATA_FOLDER)
    clean_data(DATA_FOLDER)
