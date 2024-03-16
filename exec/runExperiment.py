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

from src.Visualization import DrawBackground, DrawNewState, DrawImage, DrawText, DrawLinkImage
from src.Controller import HumanControllerNoUpdate, NormalNoise, AwayFromTheGoalNoise, CheckBoundary
from src.UpdateWorld import *
from src.Writer import WriteDataFrameToCSV
from src.Trial import NormalTrialSyn, SpecialTrialSyn
from src.Experiment import Experiment


def main():
    experimentValues = co.OrderedDict()

    isTestTrial = 0
    if isTestTrial:
        experimentValues["pair"] = 0
        experimentValues["namePlayer1"] = "test1"
        experimentValues["namePlayer2"] = "test2"
    else:
        experimentValues["pair"] = 1 # start from 1
        experimentValues["namePlayer1"] = "subjName1-age"
        experimentValues["namePlayer2"] = "subjName2-age"

    picturePath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Pictures/'
    resultsPath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/results/'
    writerPath = resultsPath + 'realTime-unSynPair' + str(experimentValues["pair"]) + '_' + experimentValues["namePlayer1"] + '.csv'
    writer = WriteDataFrameToCSV(writerPath)


    dimension = 15
    minDistanceBetweenGrids = 5
    keyPressInterval = 0

    bottom = [4, 6, 8]
    height = [5, 6, 7]
    shapeDesignValues = createShapeDesignValue(bottom, height)

    noiseCondition = list(permutations([1, 2, 0], 3))
    noiseCondition.append((1, 1, 1))

    blockNumber = 3
    noiseDesignValuesPlayer1 = createNoiseDesignValue(noiseCondition, blockNumber)
    noiseDesignValuesPlayer2 = createNoiseDesignValue(noiseCondition, blockNumber)

    # no noise
    noiseDesignValuesPlayer1 = noiseDesignValuesPlayer2 = [0]*len(noiseCondition)

    direction = [0, 90, 180, 270]
    updateWorld = UpdateWorld(direction, dimension)

    pg.init()
    screenWidth = 800
    screenHeight = 800
    fullscreen = False
    if fullscreen:
        screen = pg.display.set_mode((screenWidth, screenHeight), pg.FULLSCREEN)
    else:
        screen = pg.display.set_mode((screenWidth, screenHeight))

    pg.display.init()
    pg.fastevent.init()
    leaveEdgeSpace = int(1 / 300 * screenWidth)
    lineWidth = int(1 / 600 * screenWidth)
    backgroundColor = [255, 255, 255]
    lineColor = [0, 0, 0]
    targetColor = [255, 50, 50]

    playerColor = [0, 155, 50]
    player2Color = [50, 50, 255]
    targetRadius = int(1 / 60 * screenWidth)
    playerRadius = int(1 / 60 * screenWidth)
    textColorTuple = (255, 50, 50)
    textSize = int(1 / 14 * screenWidth)

    introductionImage = pg.image.load(picturePath + 'introduction.png')
    readyImage = pg.image.load(picturePath + 'ready.png')
    windImage = pg.image.load(picturePath + 'leftwind.png')
    finishImage = pg.image.load(picturePath + 'finish.png')

    introductionImage = pg.transform.scale(introductionImage, (screenWidth, screenHeight))
    readyImage = pg.transform.scale(readyImage, (screenWidth, screenHeight))
    finishImage = pg.transform.scale(finishImage, (screenWidth, screenHeight))

    drawBackground = DrawBackground(screen, dimension, leaveEdgeSpace, backgroundColor, lineColor, lineWidth, textColorTuple)
    drawText = DrawText(screen, drawBackground, textSize)
    drawNewState = DrawNewState(screen, drawBackground, targetColor, playerColor, player2Color, targetRadius, playerRadius, windImage)
    drawImage = DrawImage(screen)
    drawLinkImage = DrawLinkImage(screen)

    humanController = HumanControllerNoUpdate(dimension)
    checkBoundary = CheckBoundary([0, dimension - 1], [0, dimension - 1])
    controller = humanController
    normalNoise = NormalNoise(controller)
    awayFromTheGoalNoise = AwayFromTheGoalNoise(controller)
    normalTrial = NormalTrialSyn(controller, drawNewState, drawText, normalNoise, checkBoundary, keyPressInterval)
    specialTrial = SpecialTrialSyn(controller, drawNewState, drawText, awayFromTheGoalNoise, checkBoundary, keyPressInterval)
    experiment = Experiment(normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath)
    drawImage(introductionImage)

    if not isTestTrial:
        drawLinkImage(readyImage, 5000)

    experiment(noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues)
    drawImage(finishImage)


if __name__ == "__main__":
    main()
