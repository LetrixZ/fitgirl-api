import requests, json, re
from bs4 import BeautifulSoup
#from app import *

tracker = "https://1337x.to"

def get_torrent_entries(url, pageNumber):
    page = requests.get(tracker + url + str(pageNumber) + '/')
    soup = BeautifulSoup(page.content, 'html.parser')
    entries = soup.find('table', {"class": "table-list"}).findAll('tr')
    entries.pop(0)
    if url.find('FitGirl-torrents') != -1:
        return entries
    if soup.find('div', {'class':'pagination'}).find('li', {'class':'last'}):
        pageNumber += 1
        print(tracker + url + str(pageNumber) + '/')
        tmp = get_torrent_entries(url, pageNumber)
        tmp.pop(0)
        entries += tmp
    entries[:] = [e for e in entries if e.find('td', {'class':'coll-5'}).find('a').getText() == 'FitGirl']
    return entries

def parse(entries):
    entries = entries
    torrents = []
    for e in entries:
        torrent = {}
        nameCode = e.find('td', {'class':'coll-1'}).findAll('a')[1]
        nameText = nameCode.getText()
        if nameText.find('(') != -1:
            name = nameText[:nameText.find('(')-1]
        elif nameText.find('[') != -1:
            name = nameText[:nameText.find('[')-1]
        seeds = e.find('td', {'class':'coll-2'}).getText()
        leeches = e.find('td', {'class':'coll-3'}).getText()
        size = e.find('td', {'class':'coll-4'}).getText()
        if size.find(' MB') != -1:
            size = str(float(size[:-5])/1000)
        else:
            size = size[:-5]
        torrent['url'] = 'https://1337x.to'+nameCode.get('href')
        torrent['name'] = name
        torrent['size'] = size
        torrent['seeds'] = seeds
        torrent['leeches'] = leeches
        torrents.append(torrent)
    return torrents

def search_torrents(search):
    return(parse(get_torrent_entries('/category-search/'+search+' FitGirl/Games/', 1)))

def latest_torrents():
    return(parse(get_torrent_entries('/FitGirl-torrents/', 1)))