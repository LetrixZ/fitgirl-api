# app.py
import requests, re, time, asyncio, aiohttp
from flask import Flask, jsonify, json
from bs4 import BeautifulSoup
from operator import itemgetter
from gamedata import game_data
from torrents import search_torrents, latest_torrents

base_url = '/api/v1'
fitgirl = 'https://fitgirl-repacks.site/'

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

def get_bodies(urlList):
    bodies = []
    async def get(url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    resp = await response.read()
                    print("Successfully got url {} with response of length {}.".format(url, len(resp)))
                    if len(resp) > 1000:
                        bodies.append(resp)
        except Exception as e:
            print("Unable to get url {} due to {}.".format(url, e.__class__))
    async def main(urls, amount):
        ret = await asyncio.gather(*[get(url) for url in urls])
        print("Finalized all. ret is a list of len {} outputs.".format(len(ret)))
    urls = urlList
    amount = len(urls)
    start = time.time()
    asyncio.run(main(urls, amount))
    end = time.time()
    print("Took {} seconds to pull {} websites.".format(end - start, amount))
    return bodies

def get_entries(searchTerm, page):
    body = get_body('page/'+str(page)+'/?s='+searchTerm)
    regex = re.compile('.*repack.*')
    entries = body.find_all('article', {"class": regex})
    if body.find_all("a", {'class':'next'}):
        page += 1
        if page > 2:
            return entries
        entries += get_entries(searchTerm, page)
    return entries

@app.route(base_url+'/game/<string:gameID>')
def gameData(gameID):
    start_time = time.time()
    body = get_body(gameID)
    gameData = game_data(body)
    print("--- %s seconds ---" % (time.time() - start_time))
    return return_json(gameData)

@app.route(base_url+'/search/<string:searchTerm>')
def searchData(searchTerm):
    start_time = time.time()
    entries = get_entries(searchTerm, 1)
    games = []
    urlList = [(fitgirl+x.find('h1', {'class':'entry-title'}).find('a').get('href')[29:-1]) for x in entries]
    bodies = get_bodies(urlList)
    for body in bodies:
        soup =  BeautifulSoup(body, 'html.parser')
        gameData = game_data(soup)
        if gameData is None:
        	continue
        games.append(gameData)
    """for entry in entries:
        gameID = entry.find('h1', {'class':'entry-title'}).find('a').get('href')[29:-1]
        gameData = game_data(get_body(gameID))
        games.append(gameData)"""
    games = sorted(games, key=itemgetter('date'))
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
    default_dict = {"message" : "Fitgirl-Repacks unnoficial api.", "author": "u/LetrixZ", "entries": 
    [{'Search games on Fitgirl (first 2 pages)':'/api/v1/search/:game/', 'Get game download links by ID':'/api/1/game/:id','Search FitGirl torrents on 1337x':'/api/v1/torrents/search/:game','Latest FitGirl torrents on 1337x':'/api/v1/torrents/latest'}]}
    return return_json(default_dict)

@app.route("/")
def index():
    default_dict = {"message" : "🏴‍☠️🦜"}
    return return_json(default_dict)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=False)
