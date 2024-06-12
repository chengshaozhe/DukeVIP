import pygame as pg
import os
import pandas as pd
import collections as co
import numpy as np
import pickle
from random import shuffle, choice
from itertools import permutations
import sys
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..')))

from src.Visualization import DrawBackground, DrawNewState1P2G, DrawImage, DrawText
from src.Controller import SingleController, NormalNoise, AwayFromTheGoalNoise, CheckBoundary
from src.UpdateWorld import *
from src.Writer import WriteDataFrameToCSV
from src.Trial import NormalTrial1P2G, SpecialTrial1P2G
from src.Experiment import ExperimentBumps


def main():
    gridSize = 15
    noise = 0

    picturePath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Pictures/'
    resultsPath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Results/'

    bottom = [4, 6, 8]
    height = [6, 7, 8]
    shapeDesignValues = createShapeDesignValue(bottom, height)
    noiseCondition = list(permutations([1, 2, 0], 3))
    noiseCondition.append((1, 1, 1))
    blockNumber = 3
    noiseDesignValues = createNoiseDesignValue(noiseCondition, blockNumber)
    direction = [0, 90, 180, 270]
    updateWorld = UpdateWorld1P2G(direction, gridSize)


    numberOfTrials = 10
    # no noise
    if noise == 0:
        noiseDesignValues = [0]*numberOfTrials

    pg.init()
    screenWidth = 800
    screenHeight = 800
    screen = pg.display.set_mode((screenWidth, screenHeight))
    leaveEdgeSpace = 2
    lineWidth = 1
    backgroundColor = [255, 255, 255]
    lineColor = [0, 0, 0]
    targetColor = [255, 50, 50]
    playerColor = [50, 50, 255]
    targetRadius = int(1/60 * screenWidth)
    playerRadius = int(1/60 * screenWidth)
    textColorTuple = (255, 50, 50)
    textSize = int(1/14 * screenWidth)

    experimentValues = co.OrderedDict()
    experimentValues["name"] = 'test'
    writerPath = resultsPath + "1P2G-NoBumps-"+ experimentValues["name"] + '.csv'
    writer = WriteDataFrameToCSV(writerPath)
    introductionImage = pg.image.load(picturePath + 'introduction.png')
    finishImage = pg.image.load(picturePath + 'finish.png')
    windImage = pg.image.load(picturePath + 'leftwind.png')
    readyImage = pg.image.load(picturePath + 'ready.png')

    introductionImage = pg.transform.scale(introductionImage, (screenWidth, screenHeight))
    # readyImage = pg.transform.scale(readyImage, (screenWidth, screenHeight))
    # finishImage = pg.transform.scale(finishImage, (screenWidth, screenHeight))
    drawBackground = DrawBackground(screen, gridSize, leaveEdgeSpace, backgroundColor, lineColor, lineWidth, textColorTuple)
    drawText = DrawText(screen, drawBackground, textSize)
    drawNewState = DrawNewState1P2G(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)
    drawImage = DrawImage(screen)

    actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    keyBoradActionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}

    humanController = SingleController(keyBoradActionDict)
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])
    controller = humanController
    normalNoise = NormalNoise(controller)
    awayFromTheGoalNoise = AwayFromTheGoalNoise(controller)
    normalTrial = NormalTrial1P2G(controller, drawNewState, drawText, normalNoise, checkBoundary)
    specialTrial = SpecialTrial1P2G(controller, drawNewState, drawText, awayFromTheGoalNoise, checkBoundary)
    experiment = ExperimentBumps(normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath)
    # drawImage(introductionImage)
    drawImage(readyImage)
    experiment(noiseDesignValues, shapeDesignValues)
    drawImage(finishImage)


if __name__ == "__main__":
    main()
