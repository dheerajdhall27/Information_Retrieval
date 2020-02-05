import json
import sys
import glob
import re
import nltk

"""
Global data structures and values used inside the program
"""
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
Sets the Total Frequency dictionary to empty
"""


def reinitializeDict():
    global totalFrequencyDict
    totalFrequencyDict.clear()


"""
Extract all the files from a folder and append it to a list.
"""


def extractFileInformation(files):
    fileData = []
    for file in files:
        data = open(file, 'r')
        fileData.append(data.read())

    return fileData


"""
Creates the Freaquenct dictionary (Positive and Negative review frequency dictionary)
"""


def getFrequencyDict(files):
    dataDict = {}

    for f in files:
        removedData = re.sub('[^a-zA-Z.\d\s]', '', f)
        data = nltk.bigrams(removedData.split())

        for d in data:
            bigram = d[0] + " " + d[1]
            dataDict[bigram] = dataDict.get(bigram, 0) + 1

    return dataDict


"""
This method is used to add to the Total Frequency dictionary
"""


def addToTotalFrequency(negativeDict, positiveDict):
    wordDict = negativeDict.copy()

    for key in positiveDict.keys():
        wordDict[key] = wordDict.get(key, 0) + positiveDict[key]

    return wordDict


"""
Updates negative and positive dictionaries to contains the same number of values
"""


def updateNegativeAndPositiveDictionary():
    global totalFrequencyDict, positiveFrequencyDict, negativeFrequencyDict
    for key in totalFrequencyDict.keys():
        positiveFrequencyDict[key] = positiveFrequencyDict.get(key, 0)
        negativeFrequencyDict[key] = negativeFrequencyDict.get(key, 0)


"""
Removes the words with frequency below 5
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
Removes the words with frequency below 5
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
This method uses the Laplace smoothing
"""


def calcuateProbabilitiesByAddingSmoothing():
    global negWordCount, posWordCount, negativeFrequencyDict, positiveFrequencyDict, totalFrequencyDict
    total = totalFrequencyDict.__len__()

    for key in negativeFrequencyDict.keys():
        negativeProbabilityDict[key] = (negativeFrequencyDict[key] + 1) / (negWordCount + total)

    for key in positiveFrequencyDict.keys():
        positiveProbabilityDict[key] = (positiveFrequencyDict[key] + 1) / (posWordCount + total)


"""
This method is used to apply the DIRICHLET Smoothing
"""


def calcuateProbabilitiesByAddingDirichletSmoothing():
    global negWordCount, posWordCount, negativeFrequencyDict, positiveFrequencyDict, totalFrequencyDict

    mew = 0.2

    for key in negativeFrequencyDict.keys():
        negativeProbabilityDict[key] = \
            ((negativeFrequencyDict[key] + (mew * (totalFrequencyDict[key] / (posWordCount + negWordCount))))) / (
                    negWordCount + mew)

    for key in positiveFrequencyDict.keys():
        positiveProbabilityDict[key] = \
            ((positiveFrequencyDict[key] + (mew * (totalFrequencyDict[key] / (posWordCount + negWordCount))))) / (
                    posWordCount + mew)


"""
This method is used to apply the JELINEK-MERCER Smoothing
"""


def calcuateProbabilitiesByAddingJMSmoothing():
    global negWordCount, posWordCount, negativeFrequencyDict, positiveFrequencyDict, totalFrequencyDict

    lValue = 0.5
    for key in negativeFrequencyDict.keys():
        negativeProbabilityDict[key] = ((1 - lValue) * (negativeFrequencyDict[key] / negWordCount)) + (
                lValue * (totalFrequencyDict[key] / (negWordCount + posWordCount)))

    for i in positiveFrequencyDict.keys():
        positiveProbabilityDict[i] = ((1 - lValue) * (positiveFrequencyDict[i] / posWordCount)) + (
                lValue * (totalFrequencyDict[i] / (negWordCount + posWordCount)))


"""
The main method which uses helper to extract the information and write to a file
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

    # calcuateProbabilitiesByAddingSmoothing()
    calcuateProbabilitiesByAddingDirichletSmoothing()
    # calcuateProbabilitiesByAddingJMSmoothing()


    mainProbData = [negativeProbabilityDict, positiveProbabilityDict]
    model_file = open(outputPath, "w")
    json.dump(mainProbData, model_file)


"""
This is the main driver program. Thi program is to classify using NAIVE BAYES, where it utilizes
bigrams and removes special characters
"""


def main():
    filesDirectoy = sys.argv[1]
    outputPath = sys.argv[2]

    extractInformation(filesDirectoy, outputPath)


main()
