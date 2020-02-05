import math
import operator

dampingFactor = 0.85

SinkNodeSet = set()
Pages = {}
MainDictionary = {}
OutLinkDictionary = {}

PageRank = {}
NewPageRank = {}

previousPerplexity = 0
perplexityCount = 0

Perplexities = []

"""
This Method is used to add all the pages to the Pages (P) dictionary.
"""


def getAllPages():
    with open("vertices-edu.txt", "r") as pageFile:
        for line in pageFile.readlines():
            data = line.split(" ")
            pageIndex = data[0]
            pageDomain = data[1].split("\n")[0]
            Pages[pageIndex] = pageDomain


""" 
This method is used to update the edges related information.
It creates an adjacency list for the nodes that have edges pointing to them.
"""


def addEdgesInformation():
    with open("edges-edu.txt", "r") as edgesFile:
        for line in edgesFile.readlines():
            data = line.split(" ")
            fromNode = data[0]
            toNode = data[1].split("\n")[0]
            if toNode not in MainDictionary.keys():
                nodeSet = set()
                nodeSet.add(fromNode)
                MainDictionary[toNode] = nodeSet
            else:
                MainDictionary[toNode].add(fromNode)
            updateNumberOfOutLinks(fromNode)


"""
This method Updates the number of out links for each node from edges data
"""


def updateNumberOfOutLinks(fromNode):
    if fromNode in OutLinkDictionary:
        OutLinkDictionary[fromNode] = OutLinkDictionary[fromNode] + 1
    else:
        OutLinkDictionary[fromNode] = 1


"""
This Method is used to calculate the total sink nodes
"""


def calculateSinkNodes():
    for key in Pages.keys():
        if key not in OutLinkDictionary.keys() and key not in MainDictionary.keys():
            SinkNodeSet.add(key)


"""
This method is used to run the PageRank algorithm
"""


def pageRank():
    length = len(Pages)
    for p in Pages:
        PageRank[p] = 1 / length
    iterations = 0
    while not isConverging():
        iterations = iterations + 1
        sinkPR = 0
        for sinkPage in SinkNodeSet:
            sinkPR += PageRank[sinkPage]
        for page in Pages:
            NewPageRank[page] = (1 - dampingFactor) / length
            NewPageRank[page] = NewPageRank[page] + dampingFactor * (sinkPR / length)

            if page in MainDictionary.keys():
                for node in MainDictionary[page]:
                    NewPageRank[page] = NewPageRank[page] + dampingFactor * ((PageRank[node]) /
                                                                             OutLinkDictionary[node])
        for p in Pages:
            PageRank[p] = NewPageRank[p]

    return PageRank


"""
This method is used to check if the page rank is converging
"""


def isConverging():
    global previousPerplexity
    global perplexityCount

    count = 0
    for p in PageRank.values():
        count += p * math.log(p, 2)
    count = -count
    currentPerplexity = math.pow(2, count)
    if previousPerplexity == 0:
        previousPerplexity = currentPerplexity
        Perplexities.append(currentPerplexity)
        return False
    else:
        if abs(currentPerplexity - previousPerplexity) < 1:
            perplexityCount = perplexityCount + 1
            if perplexityCount == 4:
                return True
            return False
        else:
            perplexityCount = 0
    previousPerplexity = currentPerplexity
    Perplexities.append(currentPerplexity)
    return False


"""
This method prints the Top 50 Page websites in descending order.
"""


def getTopFiftyPageRanks(data):
    UnsortedPageRank = {}
    for p in data.keys():
        UnsortedPageRank[PageRank[p]] = p

    SortedPageRank = dict(sorted(UnsortedPageRank.items(), key=operator.itemgetter(0), reverse=True))

    iteration = 0
    topFiftyPageRanks = []
    for PR in SortedPageRank:
        topFiftyPageRanks.append(PR)
        print("documentID: " + str(SortedPageRank[PR]) + ", Website Domain: " + str(
            Pages[SortedPageRank[PR]]) + ",  Page Rank: " + str(PR))
        iteration = iteration + 1
        if iteration == 50:
            break
    return topFiftyPageRanks


"""
This method prints the Websites with in-link counts and returns a List with 50 values.
"""


def getWebsitesWithInlinkCounts():
    inLinkDictionary = {}

    for page in MainDictionary.keys():
        inLinkDictionary[page] = len(MainDictionary[page])

    SortedInlink = dict(sorted(inLinkDictionary.items(), key=operator.itemgetter(1), reverse=True))

    iteration = 0
    for SIL in SortedInlink.keys():
        print("documentID: " + str(SIL) + ", Website domain: " + str(Pages[SIL]) + ", In-Link Count: " + str(
            inLinkDictionary[SIL]))
        iteration = iteration + 1
        if iteration == 50:
            break


"""
This method is used to get the proportion of websites which have no inlinks
"""


def getTheProportionOfWebsitesWithNoInLinks():
    numberWithoutInLinks = len(Pages) - len(MainDictionary)
    return numberWithoutInLinks / len(Pages)


"""
This method calculates the proportion of websites which have no outlinks.
"""


def getTheProportionOfWebsitesWithNoOutLinks():
    numberWithoutOutLinks = len(Pages) - len(OutLinkDictionary)
    return numberWithoutOutLinks / len(Pages)


def getTheProportionOfPageRankLessThanOriginal(data):
    originalValue = 1 / len(Pages)

    count = 0
    for rank in data.keys():
        if PageRank[rank] < originalValue:
            count = count + 1
    return count / len(PageRank)


"""
This method Prints all data
"""


def printAllData(data):
    print("PERPLEXITY VALUES: " + str(Perplexities))
    print("\n")
    print("TOP 50 PAGE RANKS:")
    getTopFiftyPageRanks(data)
    print("\n")
    print("TOP 50 INLINK COUNT:")
    getWebsitesWithInlinkCounts()
    print("\n")
    print("PROPORTION OF WEBSITES WITH NO INLINKS:" + str(getTheProportionOfWebsitesWithNoInLinks()))
    print("PROPORTION OF WEBSITES WITH NO OUTLINKS:" + str(getTheProportionOfWebsitesWithNoOutLinks()))
    print("PROPORTIONS OF PAGE RANK LESS THAN ORIGINAL: " + str(getTheProportionOfPageRankLessThanOriginal(data)))


"""
This is the main driver method
"""


def main():
    getAllPages()
    addEdgesInformation()
    calculateSinkNodes()
    data = pageRank()
    printAllData(data)

main()
