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

    scoreboard = soup.select_one('score-board.scoreboard')
    title = scoreboard.select_one('.scoreboard__title').text
    print(title)
    info = scoreboard.select_one('.scoreboard__info').text
    split = info.split(', ')
    genres = split[1].split('/')
    runtime = pd.Timedelta(split[2])        # Could also use datetime.timedelta. Maybe parse the string datetime.datetime.strptime or dateutil.parser
    tomato = int(scoreboard.get('tomatometerscore')) if scoreboard.get('tomatometerscore') else 0
    audience = int(scoreboard.get('audiencescore')) if scoreboard.get('audiencescore') else 0
    # defaults to 0 if fewer than 50 reviews for the movie. could also be None or NaN or something and then maybe it gets filtered out later.

    return [title, genres, runtime, tomato, audience]

def getMovies(links, workers=5):
    # with ThreadPoolExecutor(workers) as exec:
    #     return exec.map(getMovie, links)
    movies = []
    for l in links:
        movies.append(getMovie(l))
    return movies

if __name__ == '__main__':
    # print(getMovie('https://www.rottentomatoes.com/m/yes_god_yes'))
    links = getMovieLinks(2020)
    data = getMovies(links)
    df = pd.DataFrame(data, columns=['Title', 'Genres', 'Runtime', 'Tomato %', 'Audience %'])
    print(df.head)
