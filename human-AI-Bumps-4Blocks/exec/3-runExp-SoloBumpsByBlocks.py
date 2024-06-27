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

from src.Visualization import DrawBackground, DrawNewState1P2G, DrawImage, DrawText,DrawLinkImage
from src.Controller import SingleController,PushForwardNoise, PullBackNoise,ForceToCommitNoise, CheckBoundary
from src.UpdateWorld import *
from src.Writer import WriteDataFrameToCSV
from src.Trial import Trial4Blocks
from src.Experiment import ExperimentBumps4Blocks


def main():
# game design
    gridSize = 15

    # bottom = [4, 6, 8]
    bottom = [8]
    height = [6, 7, 8]
    shapeDesignValues = createShapeDesignValue(bottom, height)
    direction = [0, 90, 180, 270]

    updateWorld = UpdateWorld1P2G(direction, gridSize)

    noiseTypes = ["pushForward", "pullBack", "forceCommit", "noNoise"]
    # noiseTypes = ["forceCommit"]

    trialsPerBlock = 2
    noiseDesignValues = [i for i in noiseTypes for _ in range(trialsPerBlock)]
    random.shuffle(noiseDesignValues)

# viz
    pg.init()
    screenWidth = 800
    screenHeight = 800
    screen = pg.display.set_mode((screenWidth, screenHeight))
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
    introductionImage = pg.image.load(picturePath + 'introduction.png')
    finishImage = pg.image.load(picturePath + 'finish.png')
    readyImage = pg.image.load(picturePath + 'ready.png')

    introductionImage = pg.transform.scale(introductionImage, (screenWidth, screenHeight))
    drawBackground = DrawBackground(screen, gridSize, leaveEdgeSpace, backgroundColor, lineColor, lineWidth, textColorTuple)
    drawText = DrawText(screen, drawBackground, textSize)
    drawNewState = DrawNewState1P2G(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)
    drawImage = DrawImage(screen)
    drawLinkImage = DrawLinkImage(screen)

#data store
    resultsPath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/results/'
    experimentValues = co.OrderedDict()
    experimentValues["name"] = 'test'
    writerPath = resultsPath + "Solo-Bumps-" + experimentValues["name"] + '.csv'
    writer = WriteDataFrameToCSV(writerPath)

#game flow
    actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    keyBoradActionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
    controller = SingleController(keyBoradActionDict)
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])


    pushForwardNoise = PushForwardNoise(controller)
    pullBackNoise = PullBackNoise(controller)
    forceToCommitNoise = ForceToCommitNoise(controller)

    trial = Trial4Blocks(controller, drawNewState, drawText, checkBoundary, pushForwardNoise, pullBackNoise, forceToCommitNoise)

    experiment = ExperimentBumps4Blocks(trial, writer, experimentValues, updateWorld, drawImage, resultsPath)

# start
    # drawImage(introductionImage)
    drawImage(readyImage)
    experiment(noiseDesignValues, shapeDesignValues)
    drawImage(finishImage)


if __name__ == "__main__":
    main()
