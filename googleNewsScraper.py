#!/Users/rosen59250/Desktop/AllCodingStuffs/APIPageFlaskWebsite/bin/python3.8
# Example search https://news.google.com/search?q=CNN&hl=en-US&gl=US&ceid=US:en

# Classes:
# Article
# Title and link are in this: ipQwMb ekueJc gEATFF RD0gLb
# Link in this: VDXfz
# Beginning of article: xBbh9
# Image: tvs3Id QwxBBf
# Publisher: wEwyrc AVN2gc uQIVzc Sksgp
# Time (in a datetime element): WW6dff uQIVzc Sksgp


import requests
from bs4 import BeautifulSoup
import random


def searchGNews(query, timeRange='', excluding='', requiring=''):
    if excluding != '':
        excluding = ' -' + excluding
    if timeRange != '':
        timeRange = ' when:' + timeRange
    if requiring != '':
        timeRange = ' "' + requiring + '"'
    URL = 'https://news.google.com/search?q=' + str(query) + requiring + timeRange + excluding +'&hl=en-US&gl=US&ceid=US:en'
    print(URL)
    try:
        page = requests.get(URL)
    except:
        data = {}
        data['status'] = 'error'
        data['error'] = 'network error server side.' \
                        'contact us on our support page to let' \
                        'us know about the issue'
        data['articlesFound'] = 0
        data['articles'] = []
        return data
    try:
        print("made it here")
        soup = BeautifulSoup(page.text, 'lxml')
        print("soup")
        articles = soup.find_all('div', class_='NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc')
        print("articles")
    except:
        data = {}
        data['status'] = 'error'
        data['error'] = 'error collecting data'
        data['articlesFound'] = 0
        data['articles'] = []
        return data

    # newId = str(binascii.b2a_hex(os.urandom(30)))
    # newId = newId.strip("b'")
    # newId = newId.strip("'")
    # filename = str(newId) + '.json'
    data = {}
    data['status'] = 'searching'
    data['error'] = None
    data['articlesFound'] = len(articles)
    numArticles = 0
    data['articles'] = []
    if len(articles) < 1:
        data['status'] = 'error'
        data['error'] = 'no articles found'
        return data
    for article in articles:
        numArticles += 1

        title_elem = article.find('h3', class_='ipQwMb ekueJc RD0gLb')
        article_link = article.find('a', class_='DY5T1d')
        article_snippet = article.find('span', class_='xBbh9')
        image_url = article.find('img', class_='tvs3Id QwxBBf')

        publisher = article.find('a', class_='wEwyrc AVN2gc uQIVzc Sksgp')
        time = article.find('time', class_='WW6dff uQIVzc Sksgp')

        url = article_link['href'].replace('./', 'https://news.google.com/', 1)
        if time == None:
            data['articles'].append({
                "source": publisher.text,
                "title": title_elem.text,
                "articlePreview": article_snippet.text,
                "url": url,
                "urlToImage": image_url['src'],
                "timePublished": "Not found"})
        else:
            data['articles'].append({
                "source": publisher.text,
                "title": title_elem.text,
                "articlePreview": article_snippet.text,
                "url": url,
                "urlToImage": image_url['src'],
                "timePublished": time['datetime']})

    # with open(filename, "w") as outfile:
    #     json.dump(data, outfile)
    data['status'] = 'success'
    return data

# searchGNews('cnn')
