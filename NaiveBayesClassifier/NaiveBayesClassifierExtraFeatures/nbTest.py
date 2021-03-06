import os
import sys
import json
from math import log
import nltk

positiveToNegativeDict = {}
negativeToPositiveDict = {}

positiveWordFrequency = {}
negativeWordFrequency = {}

predictionDataDict = {}


def printTop20Helper(dataList):
    count = 0
    for data in dataList:
        count += 1
        if count > 20:
            break
        # print(data)


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

    # print("TOP 20 Positive To Negative")
    printTop20Helper(sortedPosToNegList)

    # print("\n\n\n")
    # print("TOP 20 Negative To Positive")
    printTop20Helper(sortedNegToPosList)


def getCumulativeProbabilityForTerms(data):
    positiveValue = 0
    negativeValue = 0
    for word in data:
        bigram = word[0] + " " + word[1]
        positiveValue += log(positiveWordFrequency.get(bigram, 1))
        negativeValue += log(negativeWordFrequency.get(bigram, 1))

    return positiveValue, negativeValue


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

        bigramData = nltk.bigrams(fileData.split())

        cumulativePositiveProbability, cumulativeNegativeProbability = getCumulativeProbabilityForTerms(bigramData)

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


def main():
    print(os.path.abspath(os.curdir))
    modelFile = sys.argv[1]
    filesDirectory = sys.argv[2]
    predictionFile = sys.argv[3]

    printTop20(modelFile)
    createPredictionData(filesDirectory, predictionFile)


main()
