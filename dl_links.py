import requests
from bs4 import BeautifulSoup

fitgirl = 'http://fitgirl-repacks.site/'

def get_body(url):
    page = requests.get(fitgirl + url)
    extra = None
    version = None
    soup = BeautifulSoup(page.content, 'html.parser')
    div = soup.find('div', {"class": "entry-content"})
    try:
        entries = div.findAll('ul')[0].findAll('li')
    except IndexError as err:
        entries = div.findAll('p')[1].findAll('a')
        print(err)
    if div.find('h3').find('strong').find('span'):
        version = div.find('h3').find('strong').find('span').extract().getText()
        if version.find('+') < 2:
            version = version[2:]
    for x in div.findAll('h3'):
        if x.getText().find('Download Mirrors (') != -1:
            entries_2 = div.findAll('ul')[1].findAll('a')
            extra = [entries_2, div.findAll('h3')[1].getText()[18:-1], div.findAll('h3')[2].getText()[18:-1]]
    name = div.find('h3').find('strong').getText()
    return (entries, name, version, extra)

def parse(entries):
    links = {}
    for li in entries:
        for a in li.findAll('a'):
            if links.get(a.getText()) is not None:
                links[a.getText()+"_2"]  = a.get('href')
                continue
            if (a.getText().find('JDownloader2')) != -1:
                continue
            links[a.getText()] = a.get('href')
        if len(li.findAll('a')) == 0:
            if links.get(li.getText()) is not None:
                links[li.getText()+"_2"]  = li.get('href')
                continue
            if (li.getText().find('JDownloader2')) != -1:
                continue
            links[li.getText()] = li.get('href')
    return links

def get_data(id):
    data = get_body(id)
    entries = data[0]
    game = {}
    repack = {}
    game['name'] = data[1]
    game['version'] = data[2]
    if data[3] is None:
        links = parse(entries)
        game['links'] = links
    else:
        print("Else")
        links = parse(entries)
        repack[data[3][1]]= links
        links2 = parse(data[3][0])
        repack[data[3][2]] = links2
        game['links'] = repack
    return game
