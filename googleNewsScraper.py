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
    try:
        page = requests.get(URL) # Get the html of the page
    except:
        data = {} # Create json 
        data['status'] = 'error' # Errors are bad 
        data['error'] = 'network error server side.' \
                        'contact us on our support page to let' \
                        'us know about the issue'
        data['articlesFound'] = 0 
        data['articles'] = []
        return data 
    try:
        soup = BeautifulSoup(page.text, 'lxml') # A soup of the page
        articles = soup.find_all('div', class_='NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc') # Find all the articles (certain class) 
    except:
        data = {} # Oh no another error
        data['status'] = 'error'
        data['error'] = 'error collecting data'
        data['articlesFound'] = 0
        data['articles'] = []
        return data

    data = {} # Created it for real 
    data['status'] = 'searching' # search beep boop 
    data['error'] = None
    data['articlesFound'] = len(articles) # the length of the articles 
    numArticles = 0
    data['articles'] = []
    if len(articles) < 1:
        data['status'] = 'error' # OH NO 
        data['error'] = 'no articles found' # oh phew it isn't my fault 
        return data
    for article in articles:
        numArticles += 1

        title_elem = article.find('h3', class_='ipQwMb ekueJc RD0gLb') # The title 
        article_link = article.find('a', class_='DY5T1d') # The link 
        article_snippet = article.find('span', class_='xBbh9') # The blurb 
        image_url = article.find('img', class_='tvs3Id QwxBBf') # The image url 

        publisher = article.find('a', class_='wEwyrc AVN2gc uQIVzc Sksgp') # The publisher (eg nytimes cnn) 
        time = article.find('time', class_='WW6dff uQIVzc Sksgp') # Time it was published 

        url = article_link['href'].replace('./', 'https://news.google.com/', 1) # URL 
        if time == None: # Sometimes that breaks
            data['articles'].append({
                "source": publisher.text,
                "title": title_elem.text,
                "articlePreview": article_snippet.text,
                "url": url,
                "urlToImage": image_url['src'],
                "timePublished": "Not found"})
        else: # Otherwise it isn't broken
            data['articles'].append({
                "source": publisher.text,
                "title": title_elem.text,
                "articlePreview": article_snippet.text,
                "url": url,
                "urlToImage": image_url['src'],
                "timePublished": time['datetime']})

    data['status'] = 'success' # success
    return data
