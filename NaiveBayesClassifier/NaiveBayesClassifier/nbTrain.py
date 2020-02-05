import json
import sys
import glob

negativeFileList = []
positiveFileList = []
negativeFrequencyDict = {}
positiveFrequencyDict = {}

totalFrequencyDict = {}

negativeProbabilityDict = {}
positiveProbabilityDict = {}

negWordCount = 0
posWordCount = 0

"""
Set the Dictionary back to empty
"""


def reinitializeDict():
    global totalFrequencyDict
    totalFrequencyDict.clear()


"""
Extract all the files from the directory
"""


def extractFileInformation(files):
    fileData = []
    for file in files:
        data = open(file, 'r')
        fileData.append(data.read())

    return fileData


"""
Returns a Dictionary that consists the frequency of words
"""


def getFrequencyDict(files):
    dataDict = {}

    for f in files:
        data = f.split()

        for d in data:
            dataDict[d] = dataDict.get(d, 0) + 1

    return dataDict


"""
Calculates the total frequency and adds it to a dictionarys
"""


def addToTotalFrequency(negativeDict, positiveDict):
    wordDict = negativeDict.copy()

    for key in positiveDict.keys():
        wordDict[key] = wordDict.get(key, 0) + positiveDict[key]

    return wordDict


"""
Updates the negative and positive dictionary to make sure both consist the same amount of words
"""


def updateNegativeAndPositiveDictionary():
    global totalFrequencyDict, positiveFrequencyDict, negativeFrequencyDict
    for key in totalFrequencyDict.keys():
        positiveFrequencyDict[key] = positiveFrequencyDict.get(key, 0)
        negativeFrequencyDict[key] = negativeFrequencyDict.get(key, 0)


"""
Filters the words and increase the Negative Count
"""


def filterWordsNegativeDictBelow5():
    global negativeFrequencyDict, totalFrequencyDict, negWordCount

    dictCopy = negativeFrequencyDict.copy()

    for key in dictCopy.keys():
        if totalFrequencyDict[key] < 5:
            negativeFrequencyDict.pop(key)
        else:
            negWordCount += negativeFrequencyDict[key]


"""
Filters the words and increase the Positive Count
"""


def filterWordsPositiveDictBelow5():
    global positiveFrequencyDict, totalFrequencyDict, posWordCount

    dictCopy = positiveFrequencyDict.copy()

    for key in dictCopy.keys():
        if totalFrequencyDict[key] < 5:
            positiveFrequencyDict.pop(key)
        else:
            posWordCount += positiveFrequencyDict[key]


"""
This method is used to apply the Laplace Smoothing
"""


def calcuateProbabilitiesByAddingSmoothing():
    global negWordCount, posWordCount, negativeFrequencyDict, positiveFrequencyDict, totalFrequencyDict
    total = totalFrequencyDict.__len__()

    for key in negativeFrequencyDict.keys():
        negativeProbabilityDict[key] = (negativeFrequencyDict[key] + 1) / (negWordCount + total)

    for key in positiveFrequencyDict.keys():
        positiveProbabilityDict[key] = (positiveFrequencyDict[key] + 1) / (posWordCount + total)


"""
This Method is used to extract information by breaking dow information from the individual files
"""


def extractInformation(filesDirectory, outputPath):
    global negativeFileList, positiveFileList, positiveFrequencyDict, negativeFrequencyDict, totalFrequencyDict, \
        negativeProbabilityDict, positiveProbabilityDict

    positiveFiles = glob.glob(filesDirectory + '/pos/*.txt')
    negativeFiles = glob.glob(filesDirectory + '/neg/*.txt')

    negativeFileList = extractFileInformation(negativeFiles)
    positiveFileList = extractFileInformation(positiveFiles)

    negativeFrequencyDict = getFrequencyDict(negativeFileList)
    positiveFrequencyDict = getFrequencyDict(positiveFileList)

    totalFrequencyDict = addToTotalFrequency(negativeFrequencyDict, positiveFrequencyDict)

    # Update the Dictionary according to the Total Frequency
    updateNegativeAndPositiveDictionary()

    filterWordsNegativeDictBelow5()
    filterWordsPositiveDictBelow5()

    reinitializeDict()

    totalFrequencyDict = addToTotalFrequency(negativeFrequencyDict, positiveFrequencyDict)

    calcuateProbabilitiesByAddingSmoothing()

    mainProbData = [negativeProbabilityDict, positiveProbabilityDict]
    model_file = open(outputPath, "w")
    json.dump(mainProbData, model_file)


"""
This is the main driver program
"""


def main():
    filesDirectoy = sys.argv[1]
    outputPath = sys.argv[2]

    extractInformation(filesDirectoy, outputPath)


main()
