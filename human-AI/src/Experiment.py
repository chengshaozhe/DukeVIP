import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from itertools import permutations
from random import shuffle, choice


class Experiment():
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
        for trialIndex in range(len(noiseDesignValuesPlayer1)):
            player1Grid, player2Grid, bean1Grid, bean2Grid, direction = self.updateWorld(
                shapeDesignValues[trialIndex][0], shapeDesignValues[trialIndex][1])

            goalStates = [bean1Grid, bean2Grid]
            AIPolicy = self.runAIPolicy(goalStates, obstacles=[])

            if isinstance(noiseDesignValuesPlayer1[trialIndex], int):
                results = self.normalTrial(bean1Grid, bean2Grid, player1Grid, player2Grid, noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex],AIPolicy)
            else:
                results = self.specialTrial(bean1Grid, bean2Grid, player1Grid,player2Grid,  noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex],AIPolicy)
            results["noiseNumber"] = noiseDesignValuesPlayer1[trialIndex]
            results["bottom"] = shapeDesignValues[trialIndex][0]
            results["height"] = shapeDesignValues[trialIndex][1]
            results["direction"] = direction
            response = self.experimentValues.copy()
            response.update(results)
            responseDF = pd.DataFrame(response, index=[trialIndex])
            self.writer(responseDF)

class PracExperiment():
    def __init__(self, pracTrial, writer, experimentValues, updateWorld, drawImage, resultsPath):
        self.pracTrial = pracTrial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath

    def __call__(self, shapeDesignValues):
        for trialIndex,shapeDesignValue in enumerate(shapeDesignValues) :
            player1Grid, player2Grid, bean1Grid, bean2Grid, direction = self.updateWorld(
               shapeDesignValue[0],shapeDesignValue[1])

            results = self.pracTrial(player1Grid, bean1Grid)

            response = self.experimentValues.copy()
            response.update(results)
            responseDF = pd.DataFrame(response, index=[trialIndex])
            self.writer(responseDF)
