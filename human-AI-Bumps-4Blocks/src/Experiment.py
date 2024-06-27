import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from itertools import permutations
import random


def modify_list_after_index(x, index, new_value):
    # Make a copy of the list to avoid modifying the original list directly
    modified_list = x.copy()
    # Get the original value at the specified index
    original_value = x[index]
    # Replace the value at the specified index with the new value
    modified_list[index] = new_value
    # Adjust the list to maintain the balance by looking at elements after the specified index
    for i in range(index + 1, len(modified_list)):
        if modified_list[i] == new_value:
            modified_list[i] = original_value
            break
    return modified_list


class ExperimentBumps4Blocks():
    def __init__(self, trial, writer, experimentValues, updateWorld, drawImage, resultsPath):
        self.trial = trial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath

    def __call__(self, noiseDesignValues, shapeDesignValues):

        shapeDesignValue = random.choice(shapeDesignValues)

        # for trialIndex, noiseType in enumerate(noiseDesignValues):
        for trialIndex in range(0,len(noiseDesignValues)):
            print(noiseDesignValues)

            noiseType = noiseDesignValues[trialIndex]

            results = self.experimentValues.copy()
            playerGrid, bean1Grid, bean2Grid, direction = self.updateWorld(shapeDesignValue[0], shapeDesignValue[1])

            results["initPlayer1Grid"] = str(playerGrid)
            results["target1Grid"] = str(bean1Grid)
            results["target2Grid"] = str(bean2Grid)

            trialData, trueNoiseType, ifModifedCondition = self.trial(bean1Grid, bean2Grid, playerGrid, noiseType, noiseDesignValues[trialIndex:])

            if ifModifedCondition:
                noiseDesignValues = modify_list_after_index(noiseDesignValues, trialIndex, trueNoiseType)

            results.update(trialData)
            resultsDF = pd.DataFrame(results, index=[trialIndex])
            self.writer(resultsDF)



class ExperimentJoint():
    def __init__(self, normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath, runAIPolicy):
        self.normalTrial = normalTrial
        self.specialTrial = specialTrial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath
        self.runAIPolicy = runAIPolicy

    def __call__(self, noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues):
        for trialIndex, shapeDesignValue in enumerate(shapeDesignValues) :
            results = self.experimentValues.copy()
            player1Grid, player2Grid, target1Grid, target2Grid, direction = self.updateWorld(
                shapeDesignValue[0], shapeDesignValue[1])

            results["initPlayer1Grid"] = str(player1Grid)
            results["initPlayer2Grid"] = str(player2Grid)
            results["target1Grid"] = str(target1Grid)
            results["target2Grid"] = str(target2Grid)
            # results["noiseNumber"] = noiseDesignValuesPlayer1[trialIndex]

            goalStates = [target1Grid, target2Grid]
            AIPolicy = self.runAIPolicy(goalStates, obstacles=[])

            if isinstance(noiseDesignValuesPlayer1[trialIndex], int):
                trialData = self.normalTrial(target1Grid, target2Grid, player1Grid, player2Grid, noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex], AIPolicy)
            else:
                trialData = self.specialTrial(target1Grid, target2Grid, player1Grid,player2Grid,  noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex], AIPolicy)

            results.update(trialData)
            resultsDF = pd.DataFrame(results, index=[trialIndex])
            self.writer(resultsDF)


class ExperimentBumps():
    def __init__(self, normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath):
        self.normalTrial = normalTrial
        self.specialTrial = specialTrial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath

    def __call__(self, noiseDesignValues, shapeDesignValues):
        for trialIndex in range(len(noiseDesignValues)):
            results = self.experimentValues.copy()

            playerGrid, bean1Grid, bean2Grid, direction = self.updateWorld(shapeDesignValues[trialIndex][0], shapeDesignValues[trialIndex][1])

            results["initPlayer1Grid"] = str(playerGrid)
            results["target1Grid"] = str(bean1Grid)
            results["target2Grid"] = str(bean2Grid)
            results["noiseNumber"] = noiseDesignValues[trialIndex]

            if isinstance(noiseDesignValues[trialIndex], int):
                trialData = self.normalTrial(bean1Grid, bean2Grid, playerGrid, noiseDesignValues[trialIndex])
            else:
                trialData = self.specialTrial(bean1Grid, bean2Grid, playerGrid, noiseDesignValues[trialIndex])

            results.update(trialData)
            resultsDF = pd.DataFrame(results, index=[trialIndex])
            self.writer(resultsDF)

class PracExperiment1P1G():
    def __init__(self, pracTrial, writer, experimentValues, updateWorld, drawImage, resultsPath):
        self.pracTrial = pracTrial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath

    def __call__(self, shapeDesignValues):
        for trialIndex,shapeDesignValue in enumerate(shapeDesignValues) :
            player1Grid, player2Grid, target1Grid, target2Grid, direction = self.updateWorld(
               shapeDesignValue[0],shapeDesignValue[1])

            results = self.pracTrial(player1Grid, target1Grid)

            response = self.experimentValues.copy()
            response.update(results)
            responseDF = pd.DataFrame(response, index=[trialIndex])
            self.writer(responseDF)
