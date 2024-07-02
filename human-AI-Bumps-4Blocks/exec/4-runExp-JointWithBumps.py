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

from src.Visualization import DrawBackground, DrawNewState2P2G, DrawImage, DrawText, DrawLinkImage
from src.Controller import Controller, PushForwardNoise, PullBackNoise,ForceToCommitNoise, CheckBoundary
from src.UpdateWorld import *
from src.Writer import WriteDataFrameToCSV
from src.Trial import Trial4BlocksHumanAI
from src.Experiment import ExperimentBumps4BlocksJoint
from machinePolicy.valueIteration import RunVI


def main():
    gridSize = 15

    bottom = [4, 6, 8]
    height = [5, 6, 7]
    shapeDesignValues = createShapeDesignValue(bottom, height)

    direction = [0, 90, 180, 270]
    updateWorld = UpdateWorld(direction, gridSize)

    noiseTypes = ["pushForward", "pullBack", "forceCommit", "noNoise"]
    # noiseTypes = ["forceCommit"]

    trialsPerBlock = 2

    noiseDesignValuesPlayer1 = [i for i in noiseTypes for _ in range(trialsPerBlock)]
    random.shuffle(noiseDesignValuesPlayer1)

    noiseDesignValuesPlayer2 = [i for i in noiseTypes for _ in range(trialsPerBlock)]
    random.shuffle(noiseDesignValuesPlayer2)


    pg.init()
    screenWidth = 800
    screenHeight = 800
    experimentValues = co.OrderedDict()
    experimentValues["name"] = 'test'

    fullscreen = False
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
    player2Color = [0, 155, 50]

    targetRadius = int(1/60 * screenWidth)
    playerRadius = int(1/60 * screenWidth)
    textColorTuple = (255, 50, 50)
    textSize = int(1/14 * screenWidth)

    picturePath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/pictures/'
    resultsPath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/results/'

    writerPath = resultsPath + "Joint-HumanAI-" + experimentValues["name"] + '.csv'
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
    drawNewState = DrawNewState2P2G(screen, drawBackground, targetColor, playerColor, player2Color, targetRadius, playerRadius, windImage)
    drawImage = DrawImage(screen)
    drawLinkImage = DrawLinkImage(screen)

# AI policy
    noise = 0.1
    gamma = 0.9
    goalReward = 30
    actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    noiseActionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    softmaxBeta = 2.5
    runAIPolicy = RunVI(gridSize, actionSpace, noiseActionSpace, noise, gamma, goalReward, softmaxBeta)

# Game dynamic
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])
    controller = Controller(gridSize, softmaxBeta)

    pushForwardNoise = PushForwardNoise(controller)
    pullBackNoise = PullBackNoise(controller)
    forceToCommitNoise = ForceToCommitNoise(controller)

    trial = Trial4BlocksHumanAI(controller, drawNewState, drawText, checkBoundary, pushForwardNoise, pullBackNoise, forceToCommitNoise)

    experiment = ExperimentBumps4BlocksJoint(trial, writer, experimentValues, updateWorld, drawImage, resultsPath, runAIPolicy)

    # drawImage(introductionImage) #
    # drawLinkImage(readyImage, 2000) # 5000

    drawImage(readyImage)
    experiment(noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues)
    drawImage(finishImage)


if __name__ == "__main__":
    main()
