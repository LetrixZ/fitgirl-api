# app.py
import requests, json, re
from flask import Flask
from bs4 import BeautifulSoup
from torrents import *

app = Flask(__name__)

base_url = '/api/v1'
fitgirl = 'http://fitgirl-repacks.site/'

def get_size(text):
    isMB = None
    isSelective = False
    offset = 0
    ogStart = text.find('Original Size')
    rpStart = text.find('Repack Size')
    if text[ogStart:ogStart+30].find('GB') != -1 :
        ogEnd = text[ogStart:].find('GB') + ogStart - 1
        rpEnd = text[rpStart:].find('GB') + rpStart - 1
        isMB = False
    else:
        ogEnd = text[ogStart:].find('MB') + ogStart - 1
        rpEnd = text[rpStart:].find('MB') + rpStart - 1
        isMB = True
    # Get Original Size
    ogSize = text[ogStart + 15: ogEnd]
    if isMB:
        ogSize = str(round(float(ogSize)/1000, 3))
    # Get Repack Size
    if text[rpStart:].find('[Selective Download]') != -1:
        offset = 5
        isSelective = True
    rpSize = text[rpStart + 13 + offset:rpEnd]
    if isMB:
        rpSize = str(round(float(rpSize)/1000, 3))
    return [ogSize, rpSize, isSelective]

def get_genres(text):
    grStart = text.find("Genres/Tags")
    grEnd = text.find("Compan") - 1
    genres = text[grStart + 13:grEnd].split(", ")
    return genres

def get_companies(text):
    cpStart = text.find("Compan")
    cpEnd = text.find("Language") - 1
    if text.find("Company") == -1:
        companies = (re.split("[,/\-!?:]+", text[cpStart+11:cpEnd]))
        companies = [x.strip(' ') for x in companies]
        return companies
    company = (re.split("[,/\-!?:]+", text[cpStart+8:cpEnd]))
    company = [x.strip(' ') for x in company]
    return company

def get_entries(number, game):
    page = requests.get(fitgirl+"page/"+str(number)+"/?s="+game)
    soup = BeautifulSoup(page.content, 'html.parser')
    regex = re.compile('.*repack.*')
    entries = soup.find_all('article', {"class": regex})
    if soup.find_all("a", {'class':'next'}):
        number += 1
        entries += get_entries(number, game)
    return entries

@app.route(base_url+"/search/<string:game>")
def search_games(game):
    games = []
    entries = get_entries(1, game)
    for entry in entries:
        if "-".join(entry['class']).find('tag-') != -1:
            continue
        game = {}
        id = entry.find('h1').find('a').get('href')[29:-1]
        name = entry.find('h1').find('a').getText()
        if name.find(u'\u2013') != -1:
            name = name.replace(u'\u2013','-')
        text = entry.find('p').getText()
        size = get_size(text)
        game['id'] = id
        game['name'] = name
        game['originalSize'] = size[0]
        game['repackSize'] = size[1]
        game['selectiveDownload'] = size[2]
        game['genres'] = get_genres(text)
        game['companies'] = get_companies(text)
        games.append(game)
    return json.dumps(games)

@app.route(base_url+'/torrents/search/<string:name>')
def searchTorrent(name):
    return json.dumps(search_torrents(name))

@app.route(base_url+'/torrents/latest')
def getLatestsTorrents():
    return json.dumps(latest_torrents())

@app.route(base_url+'/')
def api():
    default_dict = {"message" : "Fitgirl-Repacks unnoficial api.", "author": "Fermin Cirella (Letrix)", "entries": 
    [{'Search games on Fitgirl':'/api/v1/search/:game','Search FitGirl torrents on 1337x':'/api/v1/torrents/search/:game','Latest FitGirl torrents on 1337x':'/api/v1/torrents/latest'}]}
    return json.dumps(default_dict)

@app.route("/")
def index():
    default_dict = {"message" : "🏴‍☠️🦜"}
    return json.dumps(default_dict, ensure_ascii=False)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
