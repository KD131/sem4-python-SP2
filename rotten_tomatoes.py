from concurrent.futures import ThreadPoolExecutor
from time import sleep, time

import bs4
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


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
    # r = requests.get(link)
    # r.raise_for_status()
    # soup = bs4.BeautifulSoup(r.text, 'html.parser')
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(link)

    

    def expand_shadow_element(element):
        shadow_root = browser.execute_script('return arguments[0].shadowRoot.children', element)
        return shadow_root

    scoreboard = browser.find_element(By.CSS_SELECTOR, 'score-board.scoreboard')
    # print(scoreboard.text)
    # shadow = scoreboard.shadow_root     # would work in a chromium browser
    shadow = expand_shadow_element(scoreboard)
    print(shadow[1].text)
    return None
    # this doesn't work for some reason
    # .children is a workaround but it would work better in Chrome.

    # Running many browsers crashes the whole thing.
    # And overfills the RAM which then fills up the C drive which is real bad.
    # I think I'll have to run a single browser, and it'll just take a while.
    # Then I'll save it to a CSV.
    # And I'll need to run it in Chrome so I'll have to install the webdriver.

    title = scoreboard.find_element(By.CSS_SELECTOR, '.scoreboard__title').text
    print(title)
    info = scoreboard.find_element(By.CSS_SELECTOR, '.scoreboard__info').text
    split = info.split(', ')
    genres = split[1].split('/')
    runtime = pd.Timedelta(split[2])        # Could also use datetime.timedelta. Maybe parse the string datetime.datetime.strptime or dateutil.parser
    tomato = shadow.find_element(By.CSS_SELECTOR, '.tomatometer-container .percentage').text
    tomato = tomato[:-1]                    # removes last char which is '%'. If needed, can also strip but unnecessary here.
    audience = shadow.find_element(By.CSS_SELECTOR, '.audience-container .percentage').text
    audience = audience[:-1]

    return [title, genres, runtime, tomato, audience]

    

def getMovies(links, workers=5):
    with ThreadPoolExecutor(workers) as exec:
        return exec.map(getMovie, links)

if __name__ == '__main__':
    print(getMovie('https://www.rottentomatoes.com/m/yes_god_yes'))
    # links = getMovieLinks(2020)
    # data = getMovies(links)
    # df = pd.DataFrame(data, columns=['Title', 'Genres', 'Runtime', 'Tomato %', 'Audience %'])
    # print(df.head)
