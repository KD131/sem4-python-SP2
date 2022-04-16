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

    title = soup.select_one('.scoreboard__title').text
    info = soup.select_one('.scoreboard__info').text
    split = info.split(', ')
    genres = split[1].split('/')
    runtime = pd.Timedelta(split[2])        # Could also use datetime.timedelta. Maybe parse the string datetime.datetime.strptime or dateutil.parser
    tomato = soup.select_one('.tomatometer-container .percentage').text
    tomato = tomato[:-1]                    # removes last char which is '%'. If needed, can also strip but unnecessary here.
    audience = soup.select_one('.audience-container .percentage').text
    audience = audience[:-1]

    return [title, genres, runtime, tomato, audience]

def getMovies(links, workers=5):
    movies = []
    with ThreadPoolExecutor(workers) as exec:
        return exec.map(getMovie, links)

if __name__ == '__main__':
    links = getMovieLinks(2020)
    data = getMovies(links)
    df = pd.DataFrame(data, columns=['Title', 'Genres', 'Runtime', 'Tomato %', 'Audience %'])
    print(df.head)
