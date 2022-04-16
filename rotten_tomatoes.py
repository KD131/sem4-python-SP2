from concurrent.futures import ThreadPoolExecutor
import bs4
import pandas as pd
import requests


def getMovieLinks(year):
    base = 'https://www.rottentomatoes.com'
    url = base + '/top/bestofrt/'
    params = {'year': year}

    r = requests.get(url, params=params)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    elems = soup.select('#top_movies_main a.articleLink')
    return [base + e.get('href') for e in elems if e.get('href') and e.get('href').startswith('/')]

def getMovie(link):
    r = requests.get(link)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    title = soup.select_one('.scoreboard__title').contents
    print(title)

def getMovies(links, workers=5):
    movies = []
    with ThreadPoolExecutor(workers) as exec:
        exec.map(getMovie, links)

    # for link in links:
    #     getMovie(link)

if __name__ == '__main__':
    links = getMovieLinks(2020)
    getMovies(links)
