import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from itertools import permutations
import random


def modify_list_after_index(x, index, new_value):
    modified_list = x.copy()
    original_value = x[index]
    modified_list[index] = new_value
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
        for trialIndex in range(0, len(noiseDesignValues)):
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


class ExperimentBumps4BlocksJoint():
    def __init__(self, trial, writer, experimentValues, updateWorld, drawImage, resultsPath, runAIPolicy):
        self.trial = trial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath
        self.runAIPolicy = runAIPolicy

    def __call__(self, noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues):
        shapeDesignValue = random.choice(shapeDesignValues)

        # for trialIndex, noiseType in enumerate(noiseDesignValues):
        for trialIndex in range(0, len(noiseDesignValuesPlayer1)):
            noiseTypePlayer1 = noiseDesignValuesPlayer1[trialIndex]
            noiseTypePlayer2 = noiseDesignValuesPlayer2[trialIndex]

            print(noiseDesignValuesPlayer1)
            print(noiseDesignValuesPlayer2)

            results = self.experimentValues.copy()
            player1Grid, player2Grid, target1Grid, target2Grid, direction = self.updateWorld(
                shapeDesignValue[0], shapeDesignValue[1])

            results["initPlayer1Grid"] = str(player1Grid)
            results["initPlayer2Grid"] = str(player2Grid)
            results["target1Grid"] = str(target1Grid)
            results["target2Grid"] = str(target2Grid)

            goalStates = [target1Grid, target2Grid]
            AIPolicy = self.runAIPolicy(goalStates, obstacles=[])

            trialData, trueNoiseTypePlayer1, trueNoiseTypePlayer2, ifModifedConditionPlayer1, ifModifedConditionPlayer2  = self.trial(target1Grid, target2Grid, player1Grid, player2Grid, noiseTypePlayer1, noiseTypePlayer2, noiseDesignValuesPlayer1[trialIndex:], noiseDesignValuesPlayer2[trialIndex:], AIPolicy)

            if ifModifedConditionPlayer1:
                noiseDesignValuesPlayer1 = modify_list_after_index(noiseDesignValuesPlayer1, trialIndex, trueNoiseTypePlayer1)

            if ifModifedConditionPlayer2:
                noiseDesignValuesPlayer2 = modify_list_after_index(noiseDesignValuesPlayer2, trialIndex, trueNoiseTypePlayer2)

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
