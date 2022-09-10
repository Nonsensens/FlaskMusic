from bs4 import BeautifulSoup as bs
import requests


def parse_songs():
    html = requests.get('https://music.yandex.ru/chart')
    page = bs(html.text, 'lxml')
    song_names = [p.text for p in page.find_all('div', class_='d-track__name')]
    song_authors = [p.text for p in page.find_all('span', class_='d-track__artists')]
    songs = dict()
    for i in range(len(song_authors)):
        songs[song_authors[i]] = song_names[i]
    return songs
