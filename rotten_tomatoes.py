from concurrent.futures import ThreadPoolExecutor

import bs4
import numpy as np
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

    scoreboard = soup.select_one('score-board.scoreboard')
    title = scoreboard.select_one('.scoreboard__title').text
    
    info = scoreboard.select_one('.scoreboard__info').text
    split = info.split(', ')
    # checks if info is missing values. I could use regex to figure out what values are there, but it might not be worth the effort.
    if len(split) < 3:
        genres = np.nan
        runtime = np.nan
    else:
        genres = split[1].split('/')
        runtime = pd.Timedelta(split[2])    # Could also use datetime.timedelta. Maybe parse the string datetime.datetime.strptime or dateutil.parser

    tomato = int(scoreboard.get('tomatometerscore')) if scoreboard.get('tomatometerscore') else np.nan
    audience = int(scoreboard.get('audiencescore')) if scoreboard.get('audiencescore') else np.nan
    # NaN for missing values. Tomato and audience are missing if fewer than 50 reviews respectively.

    print([title, genres, runtime, tomato, audience])
    return [title, genres, runtime, tomato, audience]

def getMovies(links, workers=5):
    with ThreadPoolExecutor(workers) as exec:
        return exec.map(getMovie, links)

if __name__ == '__main__':
    links = getMovieLinks(2020)
    data = getMovies(links)
    df = pd.DataFrame(data, columns=['Title', 'Genres', 'Runtime', 'Tomato %', 'Audience %'])
