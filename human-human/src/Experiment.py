import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from itertools import permutations
from random import shuffle, choice


class Experiment():
    def __init__(self, normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath):
        self.normalTrial = normalTrial
        self.specialTrial = specialTrial
        self.writer = writer
        self.experimentValues = experimentValues
        self.updateWorld = updateWorld
        self.drawImage = drawImage
        self.resultsPath = resultsPath

    def __call__(self, noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues):
        trialNum = len(noiseDesignValuesPlayer1)
        for trialIndex in range(trialNum):

            player1Grid, player2Grid, bean1Grid, bean2Grid, direction = self.updateWorld(
                shapeDesignValues[trialIndex][0], shapeDesignValues[trialIndex][1])

            # debug sepcial trial
            # results = self.specialTrial(bean1Grid, bean2Grid, player1Grid,player2Grid,  noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex])

            if isinstance(noiseDesignValuesPlayer1[trialIndex], int):
                results = self.normalTrial(bean1Grid, bean2Grid, player1Grid, player2Grid, noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex])
                results["trialType"] = 'Random Disruptions'

            else:
                results = self.specialTrial(bean1Grid, bean2Grid, player1Grid,player2Grid,  noiseDesignValuesPlayer1[trialIndex], noiseDesignValuesPlayer2[trialIndex])
                results["trialType"] = 'Critical Disruption'

            results["player1Grid"] = str(player1Grid)
            results["player2Grid"] = str(player2Grid)
            results["bean1Grid"] = str(bean1Grid)
            results["bean2Grid"] = str(bean2Grid)
            response = self.experimentValues.copy()
            response.update(results)
            responseDF = pd.DataFrame(response, index=[trialIndex])
            self.writer(responseDF)
