# app.py
import requests, re
from flask import Flask, jsonify, json
from bs4 import BeautifulSoup
from torrents import latest_torrents, search_torrents
from dl_links import get_data

base_url = '/api/v1'
fitgirl = 'http://fitgirl-repacks.site/'

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

def return_json(obj):
    response = app.response_class(json.dumps(obj, sort_keys=False), mimetype=app.config['JSONIFY_MIMETYPE'])
    return response

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
        if text[rpStart:].find('~') != -1:
            rpEnd += text[rpStart:].find('~') + rpStart - rpEnd
        if text[rpStart:].find('from') != -1:
            offset = 5
        isSelective = True
    rpSize = text[rpStart + 13 + offset:rpEnd]
    print(rpSize)
    if isMB:
        rpSize = str(round(float(rpSize)/1000, 3))
    return [ogSize, rpSize, isSelective]

def get_genres(text):
    grStart = text.find("Genres/Tags")
    if grStart == -1:
        return None
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
    """for entry in entries:
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
        game['links'] = get_links(id)
        game['genres'] = get_genres(text)
        game['companies'] = get_companies(text)
        games.append(game)"""
    for entry in entries:
        game = {}
        id = entry.find('h1').find('a').get('href')[29:-1]
        game = get_data(id)
        game['id'] = id
        text = entry.find('p').getText()
        size = get_size(text)    
        game['originalSize'] = size[0]
        game['repackSize'] = size[1]      
        game['selectiveDownload'] = size[2] 
        game['genres'] = get_genres(text)
        game['companies'] = get_companies(text)
        games.append(game)
    #response = app.response_class(json.dumps(games, sort_keys=False), mimetype=app.config['JSONIFY_MIMETYPE'])
    return return_json(games)

@app.route(base_url+'/torrents/search/<string:name>')
def searchTorrent(name):
    return return_json(search_torrents(name))

@app.route(base_url+'/torrents/latest')
def getLatestsTorrents():
    return return_json(latest_torrents())

@app.route(base_url+'/')
def api():
    default_dict = {"message" : "Fitgirl-Repacks unnoficial api.", "author": "Fermin Cirella (Letrix)", "entries": 
    [{'Search games on Fitgirl':'/api/v1/search/:game','Search FitGirl torrents on 1337x':'/api/v1/torrents/search/:game','Latest FitGirl torrents on 1337x':'/api/v1/torrents/latest'}]}
    return return_json(default_dict)

@app.route("/")
def index():
    default_dict = {"message" : "🏴‍☠️🦜"}
    return return_json(default_dict)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
