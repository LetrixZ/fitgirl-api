# app.py
import requests, re, time
from flask import Flask, jsonify, json
from bs4 import BeautifulSoup
from gamedata import game_data
from torrents import search_torrents, latest_torrents

base_url = '/api/v1'
fitgirl = 'http://fitgirl-repacks.site/'

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

def return_json(obj):
    response = app.response_class(json.dumps(obj, sort_keys=False), mimetype=app.config['JSONIFY_MIMETYPE'])
    return response

def get_body(url):
    page = requests.get(fitgirl+url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

@app.route(base_url+'/game/<string:gameID>')
def gameData(gameID):
    body = get_body(gameID)
    gameData = game_data(body)
    return return_json(gameData)

@app.route(base_url+'/search/<string:searchTerm>')
def searchData(searchTerm):
    start_time = time.time()
    page = 1
    body = get_body('page/'+str(page)+'/?s='+searchTerm)
    regex = re.compile('.*repack.*')
    entries = body.find_all('article', {"class": regex})
    if body.find_all("a", {'class':'next'}):
        page += 1
        entries += get_body('page/'+str(page)+'/?s='+searchTerm).find_all('article', {"class": regex})
    games = []
    for entry in entries:
        gameID = entry.find('h1', {'class':'entry-title'}).find('a').get('href')[29:-1]
        gameData = game_data(get_body(gameID))
        games.append(gameData)
    print("--- %s seconds ---" % (time.time() - start_time))
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
