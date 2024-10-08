import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from itertools import permutations
from random import shuffle, choice


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
        for trialIndex, shapeDesignValue in enumerate(shapeDesignValues):
            results = self.experimentValues.copy()
            playerGrid, bean1Grid, bean2Grid, direction = self.updateWorld(shapeDesignValue[0], shapeDesignValue[1])

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

class ExperimentTwoBumps():
    def __init__(self, trial, writer, experimentValues, updateWorld, drawImage):
        self.trial = trial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage

    def __call__(self, noiseDesignValues, shapeDesignValues):
        shapeDesignValue = choice(shapeDesignValues)

        # for trialIndex, noiseType in enumerate(noiseDesignValues):
        for trialIndex in range(0, len(noiseDesignValues)):
            # print(noiseDesignValues)
            noiseType = noiseDesignValues[trialIndex]

            results = self.experimentValues.copy()
            playerGrid, bean1Grid, bean2Grid, direction = self.updateWorld(shapeDesignValue[0], shapeDesignValue[1])

            results["initPlayer1Grid"] = str(playerGrid)
            results["target1Grid"] = str(bean1Grid)
            results["target2Grid"] = str(bean2Grid)

            trialData, trueNoiseType = self.trial(bean1Grid, bean2Grid, playerGrid, noiseType, noiseDesignValues[trialIndex:])

            results.update(trialData)
            resultsDF = pd.DataFrame(results, index=[trialIndex])
            self.writer(resultsDF)
