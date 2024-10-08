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

from src.Visualization import DrawBackground, DrawNewState1P1G, DrawImage, DrawText, DrawLinkImage
from src.Controller import SingleController, CheckBoundary, NormalNoise
from src.UpdateWorld import *
from src.Writer import WriteDataFrameToCSV
from src.Trial import PracTrialFreePlayNoBumps
from src.Experiment import PracExperiment1P1G
from machinePolicy.valueIteration import RunVI

def main():
    gridSize = 15
    playTime = 30000

    bottom = [4, 6, 8]
    height = [5, 6, 7]
    allShapeDesignValues = createShapeDesignValue(bottom, height)

    numOfPracRounds = 1
    expDesignValues = random.sample(allShapeDesignValues, numOfPracRounds)

    direction = [0, 90, 180, 270]
    updateWorld = UpdateWorld(direction, gridSize)

    pg.init()
    screenWidth = 800
    screenHeight = 800

    experimentValues = co.OrderedDict()
    experimentValues["name"] = 'test'

    fullscreen = 0 # True or False
    if fullscreen:
        screen = pg.display.set_mode((screenWidth, screenHeight),pg.FULLSCREEN)
    else:
        screen = pg.display.set_mode((screenWidth, screenHeight))

    pg.display.init()
    pg.fastevent.init()
    leaveEdgeSpace = int(1/300 * screenWidth)
    lineWidth = int(1/600 * screenWidth)
    backgroundColor = [255, 255, 255]
    lineColor = [0, 0, 0]
    targetColor = [255, 50, 50]
    playerColor = [50, 50, 255]

    targetRadius = int(1/60 * screenWidth)
    playerRadius = int(1/60 * screenWidth)
    textColorTuple = (255, 50, 50)
    textSize = int(1/14 * screenWidth)

    picturePath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/pictures/'
    resultsPath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/results/'

    writerPath = resultsPath + "Prac-freePlay-"+ experimentValues["name"] + '.csv'
    writer = WriteDataFrameToCSV(writerPath)
    introductionImage = pg.image.load(picturePath + 'introduction.png')
    finishImage = pg.image.load(picturePath + 'finish.png')
    readyImage = pg.image.load(picturePath + 'ready.png')

    introductionImage = pg.transform.scale(introductionImage, (screenWidth, screenHeight))
    # readyImage = pg.transform.scale(readyImage, (screenWidth, screenHeight))
    # finishImage = pg.transform.scale(finishImage, (screenWidth, screenHeight))
    drawBackground = DrawBackground(screen, gridSize, leaveEdgeSpace, backgroundColor, lineColor, lineWidth, textColorTuple)
    drawText = DrawText(screen, drawBackground, textSize)
    drawNewState = DrawNewState1P1G(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)
    drawImage = DrawImage(screen)
    drawLinkImage = DrawLinkImage(screen)

# game dynamic
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])
    keyBoradActionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
    controller = SingleController(keyBoradActionDict)
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])

    pracTrial = PracTrialFreePlayNoBumps(controller, drawNewState, drawText, checkBoundary, playTime)
    experiment = PracExperiment1P1G(pracTrial, writer, experimentValues, updateWorld, drawImage, resultsPath)

# start
    # drawImage(introductionImage)
    drawImage(readyImage)
    experiment(expDesignValues)
    drawImage(finishImage)


if __name__ == "__main__":
    main()
