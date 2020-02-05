import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
import requests
from collections import deque
import time
import re
import json

visited = set()
finalList = []
breadth = 0
startTime = time.time()
frontier_size = 0

"""
Get the parsed information of the url in bytes
"""
def getParsedRequest(url):
    request = requests.get(url)
    return request


"""
scrapes the data of a url to check for the keyphrase and adds it to the frontier
"""
def checkUrl(frontier, url, keyphrase):
    soup = scrapeData(url, keyphrase)
    if soup:
        links = soup.findAll('a', href=True)
        for link in links:
            pageUrl = link.get('href')
            if pageUrl.startswith('/wiki') and checkStringFormat(pageUrl):
                pageUrl = 'https://en.wikipedia.org' + pageUrl
                if '#' in pageUrl:
                    pageUrl = pageUrl[:pageUrl.index('#')]
                if pageUrl not in visited:
                    global frontier_size
                    frontier_size = frontier_size + 1
                    frontier.append(pageUrl)
    return frontier


"""
scrapes the data of a file and adds it to the final list of urls
"""
def scrapeData(url, keyphrase):
    # time.sleep(0.5)

    data = urllib.request.urlopen(url).read().decode("utf-8")
    soup = BeautifulSoup(data, 'lxml')
    canonical = soup.find("link", rel="canonical")
    canonical = canonical.get('href')

    visited.add(canonical)

    if keyphrase == '':
        if canonical not in finalList:
            print(canonical)
            finalList.append(canonical)
            return soup
    elif re.compile(keyphrase).search(data, re.IGNORECASE):
        if canonical not in finalList:
            print(canonical)
            finalList.append(canonical)
            return soup
    return None

"""
Checks to make sure the url does not have : and Main_Page in it 
"""
def checkStringFormat(url):
    if ':' in url or 'Main_Page' in url:
        return False
    return True

"""
This is the main driver function that starts the program
"""
def main():
    startT = time.time()
    seedURL = "https://en.wikipedia.org/wiki/Karen_Sp%C3%A4rck_Jones"
    keyphrase = 'retrieval'

    frontier = deque()
    frontier.append(seedURL)
    global frontier_size
    frontier_size = frontier_size + 1
    final = crawlerThread(frontier, keyphrase)

    file = open("FocusedData.txt", "w+")
    file.write(json.dumps(final))
    print(time.time() - startT)

"""
This is the crawler thread that does a BFS crawl
"""
def crawlerThread(frontier, keyphrase):
    depth = 1
    while frontier and depth < 6:
        global frontier_size
        global visited
        while frontier_size > 0:
            url = frontier.popleft()
            if len(finalList) > 1000:
                return finalList
            if url not in visited:
                checkUrl(frontier, url, keyphrase)
            frontier_size = frontier_size - 1
        depth = depth + 1
    return finalList


main()


# data = "12345"
# index = data.index('4')
# print(index)
# print(data[:data.index('4') + 1])