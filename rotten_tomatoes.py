import os
from concurrent.futures import ThreadPoolExecutor

import bs4
import matplotlib.pyplot as plt
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
    # I could grab info from further down the page. I beleive there are also more genres there.
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

# I think I got rate limited or something. Scraping now returns 403 Forbidden.
def get_movies(year, refresh=False):
    path = f'movies_{year}.csv'
    if not os.path.exists(path) or refresh:
        links = get_movie_links(year)
        data = scrape_movies(links, year)
        df = pd.DataFrame(data)
        df.insert(4, 'Year', year)
        df.to_csv(path, index=False)
    else:
        df = pd.read_csv(path)
    return df

def plot_avg_audience_per_genre(df1, df2):
    # I concat data as a way of synchronising all datasets have the same genre columns.
    # This will be a little less tidy and more hard-coded.
    # There's probably a way to just have Pandas plot it, but I might have to go into multi-indexing or something and I don't want to deal with that.
    # Or just get the data, make a new DataFrame specifically for plotting, and just have it do it.
    # Or just do it manually.
    combined = pd.concat([df1, df2], ignore_index=True)
    genres = combined.columns[5:]
    values1 = [combined[(combined['Year'] == 2010) & combined[g].notna()]['Audience %'].mean() for g in genres]
    values2 = [combined[(combined['Year'] == 2020) & combined[g].notna()]['Audience %'].mean() for g in genres]

    n = len(genres)
    i = np.arange(n)
    w = 0.35

    fig, ax = plt.subplots()

    ax.bar(i, values1, w, label='2010')
    ax.bar(i + w, values2, w, label='2020')

    ax.set_title('Avg. audience score % per genre')
    ax.set_xticks(i + w / 2, labels=genres, rotation=45, horizontalalignment="right")

    ax.legend()
    plt.show()

# I need to redesign the dataframe. Each genre should be a column.
# An ugly solution is to just evaluate a list from the string representation. But that would still be annoying to iterate through.
# Each movie could return a single-row dataframe with the genres as columns,
# and then they would be concatted together with presumably NaN for missing values.
# Trouble is still gonna be harmonising the datasets between different years as there's no guarantee that they have the same genres.
# You could also concat those together. Then you just need a 'Year' column to separate them again.

def clean_data(data):
    mask_score = data['Tomato %'].notna() & data['Audience %'].notna()
    mask_genre = data.iloc[:, 5:].any(axis=1)
    mask_runtime = data['Runtime'].notna()
    return data[mask_score & mask_genre & mask_runtime]

def avg_runtime(data, year, genre):
    strs = data[(data['Year'] == year) & data[genre].notna()]['Runtime']
    tds = pd.to_timedelta(strs)
    return tds.mean()


if __name__ == '__main__':
    df2020 = get_movies(2020)
    df2010 = get_movies(2010)
    df1990 = get_movies(1990)

    df2020 = clean_data(df2020)
    df2010 = clean_data(df2010)
    df1990 = clean_data(df1990)

    plot_avg_audience_per_genre(df2020, df2010)

    print("Avg. runtime of dramas in 2010: " + str(avg_runtime(df2010, 2010, 'Drama')))
    print("Avg. runtime of dramas in 2020: " + str(avg_runtime(df2020, 2020, 'Drama')))
