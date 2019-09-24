import requests
from bs4 import BeautifulSoup


PWCA_URL = 'http://pwca.org/view/tour/'

def generate_tour_urls():
    return [PWCA_URL + str(x) for x in range(2010, 2020)]


if __name__ == '__main__':
    urls = generate_tour_urls()
    print(urls)