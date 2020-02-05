import os
import sys
import json
from math import log

positiveToNegativeDict = {}
negativeToPositiveDict = {}

positiveWordFrequency = {}
negativeWordFrequency = {}

predictionDataDict = {}

"""
A helper method to print the Top 20 Negative to Positive or Positive to Negative
"""


def printTop20Helper(dataList):
    count = 0
    for data in dataList:
        count += 1
        if count > 20:
            break
        print(data)


"""
Calculates the Top20 Negative to Positive and Positive to Negative
"""


def printTop20(modelFile):
    global positiveToNegativeDict, negativeToPositiveDict, positiveWordFrequency, negativeWordFrequency
    with open(modelFile) as f:
        try:
            modelData = json.load(f)
        except ValueError:
            modelData = []

    negativeWordFrequency = modelData[0]
    positiveWordFrequency = modelData[1]

    for key, value in positiveWordFrequency.items():
        valueToAdd = log(value) - log(negativeWordFrequency.get(key))
        positiveToNegativeDict[key] = valueToAdd

    sortedPosToNegList = sorted(positiveToNegativeDict.items(), reverse=True, key=lambda x: x[1])

    for key, value in negativeWordFrequency.items():
        valueToAdd = log(value) - log(positiveWordFrequency.get(key))
        negativeToPositiveDict[key] = valueToAdd

    sortedNegToPosList = sorted(negativeToPositiveDict.items(), reverse=True, key=lambda x: x[1])

    print("TOP 20 Positive To Negative")
    printTop20Helper(sortedPosToNegList)

    print("\n\n\n")
    print("TOP 20 Negative To Positive")
    printTop20Helper(sortedNegToPosList)


"""
Calculates the cumulative probability
"""


def getCumulativeProbabilityForTerms(data):
    wordData = data.split()
    positiveValue = 0
    negativeValue = 0
    for word in wordData:
        positiveValue += log(positiveWordFrequency.get(word, 1))
        negativeValue += log(negativeWordFrequency.get(word, 1))

    return positiveValue, negativeValue


"""
Main method to get calculate all data
"""


def createPredictionData(filesDirectory, outputPath):
    global predictionDataDict
    pos = []
    neg = []
    dataList = []
    for dir, subDir, files in os.walk(filesDirectory):
        for file in files:
            dataList.append(dir + "/" + file)

    for file in dataList:
        data = open(file, "r")

        fileData = data.read().replace("\n", " ")

        cumulativePositiveProbability, cumulativeNegativeProbability = getCumulativeProbabilityForTerms(fileData)

        predictionDataDict[file] = [cumulativePositiveProbability, cumulativeNegativeProbability]

        if cumulativePositiveProbability > cumulativeNegativeProbability:
            pos.append(file)
        else:
            neg.append(file)

    print("The Number of Positive Files: " + str(len(pos)))
    print("The Number of Negative Files: " + str(len(neg)))
    print("The Number of Prediction Files: " + str(len(predictionDataDict)))
    outputFile = open(outputPath, "a")
    for key, value in predictionDataDict.items():
        outputFile.write(key + ":" + "{ Positive: " + str(value[0]) + "} , { Negative: " + str(value[1]) + "}")
        outputFile.write("\n")


"""
The main driver program
"""


def main():
    print(os.path.abspath(os.curdir))
    modelFile = sys.argv[1]
    filesDirectory = sys.argv[2]
    predictionFile = sys.argv[3]

    printTop20(modelFile)
    createPredictionData(filesDirectory, predictionFile)


main()
