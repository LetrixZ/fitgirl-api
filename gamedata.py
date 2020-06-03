import re
from bs4 import BeautifulSoup

fitgirl = "https://fitgirl-repacks.site/"

def get_name(body):
    div = body.find('div', {'class':'entry-content'}).find('h3').find('strong')
    version = div.find('span').extract().getText() if div.find('span') else None
    name = div.getText()
    id = body.find('span', {'class':'entry-date'}).find('a').get('href')[29:-1]
    date = body.find('time', attrs={'datetime':True})['datetime']
    return (name, version, id, date)

def get_data(body):
    try:
        div = body.find('div', {'class':'entry-content'}).find('p')
    except Exception as e:
        print(e)
        return None
    entries = div.findAll('strong')
    index = 0
    genres = None
    if len(entries) == 5:
        index = 1
        genres = entries[0].getText().split(', ')
    companies = (re.split("[,/-]+", entries[index].getText()))
    companies = [x.strip(' ') for x in companies]
    languages = entries[index+1].getText().split('/')
    originalSize = entries[index+2].getText()
    try:
        repackSize = entries[index+3].getText() if entries[index+3].getText().find('from') else entries[index+3].getText()[5:]
    except IndexError:
        repackSize = entries[index+3].getText()[:entries[index+3].getText().find('~')-1]
    selective = ('Selective' in str(div))
    return (originalSize, repackSize, selective, genres, companies, languages)

def get_links(body):
    div = body.find('div', {'class':'entry-content'})   
    links = {}
    try:
        table = div.find('ul').findAll('li')
        for li in table:
            for a in li.findAll('a'):
                if ('JDownloader' in a.getText()): continue
                key = a.getText()
                if links.get(key): key = a.getText()+'_1'
                links[key] = a.get('href')
    except AttributeError:
        p = div.findAll('p')[1].findAll('a')
        for a in p:
            if ('JDownloader' in a.getText()): continue
            key = a.getText()
            if links.get(key): key = a.getText()+'_1'
            links[key] = a.get('href')
    return links

def get_screenshots(body):
    div = body.find('div', {'class':'entry-content'})   
    screenshots = []
    img = div.findAll('img')
    for screenshot in img:
        if ('riotpixel' in screenshot.get('src')):
            screenshots.append(screenshot.get('src'))
    return screenshots

def game_data(body):
    #body = get_body(gameID)
    data = get_data(body)
    if data is None:
        return None
    names = get_name(body)
    links = get_links(body)
    screenshots = get_screenshots(body)
    game = {'id':names[2], 'name':names[0], 'version':names[1], 'date':names[3], 'originalSize':data[0], 'repackSize':data[1], 
    'selective':data[2], 'mirrors':links, 'genres':data[3], 'companies':data[4], 'languages':data[5], 'screenshots':screenshots}
    return game

#print(game_data("call-of-duty-black-ops-3"))
#print(game_data("fifa-16-super-deluxe-edition"))
#print(game_data("fifa-18"))