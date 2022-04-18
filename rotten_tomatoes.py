import os
from concurrent.futures import ThreadPoolExecutor

import bs4
import numpy as np
import pandas as pd
import requests


def get_movie_links(year):
    base = 'https://www.rottentomatoes.com'
    url = base + '/top/bestofrt/'
    params = {'year': year}

    r = requests.get(url, params=params)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    elems = soup.select('#top_movies_main a.articleLink')
    return [base + e.get('href') for e in elems if e.get('href') and e.get('href').startswith('/')]

def get_movie(link):
    r = requests.get(link)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    scoreboard = soup.select_one('score-board.scoreboard')
    title = scoreboard.select_one('.scoreboard__title').text
    
    info = scoreboard.select_one('.scoreboard__info').text
    split = info.split(', ')
    # checks if info is missing values. I could use regex to figure out what values are there, but it might not be worth the effort.
    if len(split) < 3:
        genres = []
        runtime = np.nan
    else:
        genres = split[1].split('/')
        runtime = pd.Timedelta(split[2])    # Could also use datetime.timedelta. Maybe parse the string datetime.datetime.strptime or dateutil.parser

    tomato = int(scoreboard.get('tomatometerscore')) if scoreboard.get('tomatometerscore') else np.nan
    audience = int(scoreboard.get('audiencescore')) if scoreboard.get('audiencescore') else np.nan
    # NaN for missing values. Tomato and audience are missing if fewer than 50 reviews respectively.

    m = {'Title': title, 'Runtime': runtime, 'Tomato %': tomato, 'Audience %': audience}
    for g in genres:
        m[g] = True
    
    print(m)
    return m

def scrape_movies(links, workers=5):
    with ThreadPoolExecutor(workers) as exec:
        return exec.map(get_movie, links)

def get_movies(year):
    path = f'movies_{year}.csv'
    if not os.path.exists(path):
        links = get_movie_links(year)
        data = scrape_movies(links)
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
    else:
        df = pd.read_csv(path)
    return df

def avg_audience_per_genre(data):
    genres = data.columns[5:]
    print(genres)

# I need to redesign the dataframe. Each genre should be a column.
# An ugly solution is to just evaluate a list from the string representation. But that would still be annoying to iterate through.
# Each movie could return a single-row dataframe with the genres as columns,
# and then they would be concatted together with presumably NaN for missing values.
# Trouble is still gonna be harmonising the datasets between different years as there's no guarantee that they have the same genres.
# You could also concat those together. Then you just need a 'Year' column to separate them again.

def clean_data(data):
    mask_score = data['Tomato %'].notna() & data['Audience %'].notna()
    mask_genre = data.iloc[:, 5:].any()
    mask_runtime = data['Runtime'].notna()
    return data[mask_score & mask_genre & mask_runtime]


if __name__ == '__main__':
    df2020 = get_movies(2020)
    df2010 = get_movies(2010)
    df1990 = get_movies(1990)

    df2020 = clean_data(df2020)

    avg_audience_per_genre(df2020)
