
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

# Import necessary modules from the src directory
from src.Visualization import *
from src.Controller import *
from src.UpdateWorld import *
from src.Trial import *
from src.Experiment import *
from src.Writer import WriteDataFrameToCSV
from machinePolicy.valueIteration import RunVI

# Unified Main Function
def main():
    experimentValues = co.OrderedDict()
    experimentValues["name"] = 'test-name'

# game env
    gridSize = 15
    direction = [0, 90, 180, 270]
    bottom = [4, 6, 8]
    height = [5, 6, 7]
    allShapeDesignValues = createShapeDesignValue(bottom, height)

# setup_file_paths
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    picturePath = os.path.join(base_path, 'pictures/')
    resultsPath = os.path.join(base_path, 'results/')

# pygame init
    pg.init()
    grid_resolution = 900

    FULLSCREEN = 1
    if FULLSCREEN:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        pg.mouse.set_visible(False)
    else:
        screen = pg.display.set_mode((grid_resolution, grid_resolution))

# setup drawing
    backgroundColor = [255, 255, 255]
    targetColor = [255, 50, 50]
    playerColor = [50, 50, 255]
    player2Color = [0, 155, 50]

    targetRadius = int(1/60 * grid_resolution)
    playerRadius = int(1/60 * grid_resolution)
    textColorTuple = (255, 50, 50)
    textSize = int(1/14 * grid_resolution)

    drawBackground = DrawBackground(screen, gridSize, grid_resolution, backgroundColor)
    drawFixation = DrawFixation(screen, drawBackground)
    drawImage = DrawImage(screen)

    introImage1 = pg.transform.scale(pg.image.load(picturePath + 'intro1.png'), (grid_resolution, grid_resolution))
    introImage2 = pg.transform.scale(pg.image.load(picturePath + 'intro2.png'), (grid_resolution, grid_resolution))

    prac1Image = pg.transform.scale(pg.image.load(picturePath + 'prac1.png'), (grid_resolution, grid_resolution))
    prac2Image = pg.transform.scale(pg.image.load(picturePath + 'prac2.png'), (grid_resolution, grid_resolution))

    formal1Image = pg.transform.scale(pg.image.load(picturePath + 'diff_goal.png'), (grid_resolution, grid_resolution))


    readyImage = pg.image.load(picturePath + 'ready.png')
    finishImage = pg.image.load(picturePath + 'finish.png')

# game logic
    checkBoundary = CheckBoundary([0, gridSize - 1], [0, gridSize - 1])
    keyBoradActionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}


    # PHASE 2: Practice One Player, One Target (File 1)
    def prac1_one_player_one_target(numOfPracRounds):
        writerPath = resultsPath + "Prac-1P1G-"+ experimentValues["name"] + '.csv'
        writer = WriteDataFrameToCSV(writerPath)

        expDesignValues = random.sample(allShapeDesignValues, numOfPracRounds)

        drawNewState = DrawNewState1P1G(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)

        updateWorld = UpdateWorld(direction, gridSize)
        controller = SingleController(keyBoradActionDict)
        pracTrial = PracTrial(controller, drawNewState, drawFixation, checkBoundary)
        experiment = PracExperiment1P1G(pracTrial, writer, experimentValues, updateWorld, drawImage, resultsPath)

        drawImage(prac1Image)
        experiment(expDesignValues)
        drawImage(finishImage)


    # PHASE 3: One Player, Two Targets (File 2)
    def Prac2_one_player_two_targets(numberOfTrials):
        writerPath = resultsPath + "Exp-1P2G-NoBumps-" + experimentValues["name"] + '.csv'
        writer = WriteDataFrameToCSV(writerPath)

        shapeDesignValues = random.sample(allShapeDesignValues, numberOfTrials)
        noiseDesignValues = [0]*numberOfTrials

        drawNewState = DrawNewState1P2G(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)
        updateWorld = UpdateWorld1P2G(direction, gridSize)

        controller = SingleController(keyBoradActionDict)
        normalNoise = NormalNoise(controller)
        awayFromTheGoalNoise = AwayFromTheGoalNoise(controller)
        normalTrial = NormalTrial1P2G(controller, drawNewState, drawFixation, normalNoise, checkBoundary)
        specialTrial = SpecialTrial1P2G(controller, drawNewState, drawFixation, awayFromTheGoalNoise, checkBoundary)
        experiment = ExperimentBumps(normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath)

        drawImage(prac2Image)
        experiment(noiseDesignValues, shapeDesignValues)
        drawImage(finishImage)

    # PHASE 4: Joint Task, No Bumps (File 3)
    def formal1_joint_no_bumps(numberOfTrials):
        writerPath = resultsPath + "Exp-Joint-HumanAI-diffGoal-" + experimentValues["name"] + '.csv'
        writer = WriteDataFrameToCSV(writerPath)

        updateWorld = UpdateWorld(direction, gridSize)
        drawNewState = DrawNewState2P2G(screen, drawBackground, targetColor, playerColor, player2Color, targetRadius, playerRadius)
        drawNewStateWithArrow = DrawNewState2P2GWithArrow(screen, drawBackground, targetColor, playerColor, player2Color, targetRadius, playerRadius)

        shapeDesignValues = random.sample(allShapeDesignValues, numberOfTrials)
        noiseDesignValuesPlayer1 = noiseDesignValuesPlayer2 = [0]*numberOfTrials

        #AI policy
        noise = 0
        gamma = 0.9
        goalReward = 30
        actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        noiseActionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        softmaxBeta = 2.5
        runAIPolicy = RunVI(gridSize, actionSpace, noiseActionSpace, noise, gamma, goalReward, softmaxBeta)

        # game dynamic
        controller = Controller(gridSize, softmaxBeta)
        normalNoise = NormalNoise(controller)
        awayFromTheGoalNoise = AwayFromTheGoalNoise(controller)
        normalTrial = NormalTrialHumanAIDifferentGoal(controller, drawNewState,drawNewStateWithArrow, drawFixation, normalNoise, checkBoundary)
        specialTrial = SpecialTrialHumanAI(controller, drawNewState, drawFixation, awayFromTheGoalNoise, checkBoundary)
        experiment = ExperimentJoint(normalTrial, specialTrial, writer, experimentValues, updateWorld, drawImage, resultsPath, runAIPolicy)

        drawImage(formal1Image)
        experiment(noiseDesignValuesPlayer1, noiseDesignValuesPlayer2, shapeDesignValues)
        drawImage(finishImage)


# Execute all phases
    # phase1_free_play()
    drawImage(introImage1)
    drawImage(introImage2)

    prac1_one_player_one_target(numOfPracRounds = 5)
    Prac2_one_player_two_targets(numberOfTrials = 8)
    formal1_joint_no_bumps(numberOfTrials = 8)

    pg.quit()

if __name__ == "__main__":
    main()
