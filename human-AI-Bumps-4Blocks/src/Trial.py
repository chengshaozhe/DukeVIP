import numpy as np
import pygame as pg
from pygame import time
import collections as co
import pickle
import random

def calculateGridDis(grid1, grid2):
    gridDis = np.linalg.norm(np.array(grid1) - np.array(grid2), ord=1)
    return gridDis


def inferGoal(currentGrid, aimGrid, targetGridA, targetGridB):
    disToTargetA = calculateGridDis(currentGrid, targetGridA)
    disToTargetB = calculateGridDis(currentGrid, targetGridB)
    aimGridToTargetA = calculateGridDis(aimGrid, targetGridA)
    aimGridToTargetB = calculateGridDis(aimGrid, targetGridB)
    effortToTargetA = disToTargetA - aimGridToTargetA
    effortToTargetB = disToTargetB - aimGridToTargetB
    if effortToTargetA > effortToTargetB:
        goal = 1
    elif effortToTargetA < effortToTargetB:
        goal = 2
    else:
        goal = 0
    return goal


def checkTerminationOfTrial(bean1Grid, bean2Grid, humanGrid):
    disToTargetA = calculateGridDis(humanGrid, bean1Grid)
    disToTargetB = calculateGridDis(humanGrid, bean2Grid)

    if disToTargetA == 0 or disToTargetB == 0:
        pause = False
    else:
        pause = True
    return pause

def checkTerminationOfTrial2P2G(bean1Grid, bean2Grid, humanGrid, humanGrid2):
    if (np.linalg.norm(np.array(humanGrid) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid) - np.array(bean2Grid), ord=1) == 0) and \
            (np.linalg.norm(np.array(humanGrid2) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid2) - np.array(bean2Grid), ord=1) == 0):
        pause = False
    else:
        pause = True
    return pause

class Trial4Blocks():
    def __init__(self, controller, drawNewState, drawText, checkBoundary, pushForwardNoise ,pullBackNoise,forceToCommitNoise):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.checkBoundary = checkBoundary
        self.pushForwardNoise = pushForwardNoise
        self.pullBackNoise = pullBackNoise
        self.forceToCommitNoise = forceToCommitNoise

    def __call__(self, bean1Grid, bean2Grid, initPlayerGrid, noiseType, noiseDesignValuesRemained):
        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionList = list()
        goalList = list()
        results = co.OrderedDict()
        noiseStep = None

        trajectory = [initPlayerGrid]

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1000)
        self.drawNewState(bean1Grid, bean2Grid, initPlayerGrid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayerGrid = initPlayerGrid

        ifModifedCondition = False
        firstIntentionFlag = False
        ifnoise = False
        pause = True
        while pause:
            initialTime = time.get_ticks()
            aimPlayerGrid, aimAction = self.controller(realPlayerGrid)
            reactionTime.append(time.get_ticks() - initialTime)
            aimActionList.append(aimAction)
            stepCount = stepCount + 1

            currentGrid = trajectory[-1]
            goal = inferGoal(currentGrid, aimPlayerGrid, bean1Grid, bean2Grid)
            goalList.append(goal)

            ### decide when to focre?
            isIntentionNotRevealed = sum(goalList) == 0
            print(isIntentionNotRevealed)

            conditionCount = noiseDesignValuesRemained.count('forceCommit')
            if conditionCount != 0 and isIntentionNotRevealed and stepCount >= 3: # if no intention revealed in n steps
                noiseType = "forceCommit"
                ifModifedCondition = True

            ###
            if noiseType == "pushForward":
                noisePlayerGrid, firstIntentionFlag, realAction, noiseStep = self.pushForwardNoise(stepCount, currentGrid, bean1Grid, bean2Grid, aimAction, goal, firstIntentionFlag)

            elif noiseType == "pullBack":
                noisePlayerGrid, firstIntentionFlag, realAction, noiseStep = self.pullBackNoise(stepCount, currentGrid, bean1Grid, bean2Grid, aimAction, goal, firstIntentionFlag)

            elif noiseType == "forceCommit":
                noisePlayerGrid, firstIntentionFlag, realAction, noiseStep = self.forceToCommitNoise(stepCount, currentGrid, bean1Grid, bean2Grid, aimAction, goalList, firstIntentionFlag)

            elif noiseType == "noNoise":
                noisePlayerGrid = aimPlayerGrid

            realPlayerGrid = self.checkBoundary(noisePlayerGrid)

            trajectory.append(tuple(realPlayerGrid))
            self.drawNewState(bean1Grid, bean2Grid, realPlayerGrid)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayerGrid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])

        results["noiseType"] = noiseType
        results["reactionTime"] = str(reactionTime)
        results["trajectory"] = str(trajectory)
        results["aimAction"] = str(aimActionList)
        results["noisePoint"] = str(noiseStep)
        results["goal"] = str(goalList)

        return results, noiseType, ifModifedCondition

class Trial4BlocksHumanAI():
    def __init__(self, controller, drawNewState, drawText, checkBoundary, pushForwardNoise ,pullBackNoise,forceToCommitNoise):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.checkBoundary = checkBoundary
        self.pushForwardNoise = pushForwardNoise
        self.pullBackNoise = pullBackNoise
        self.forceToCommitNoise = forceToCommitNoise

    def __call__(self, bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, noiseTypePlayer1, noiseTypePlayer2, designValuesRemainPlayer1, designValuesRemainPlayer2, AIPolicy):

        reactionTime = list()
        trajectoryPlayer1 = [initialPlayer1Grid]
        trajectoryPlayer2 = [initialPlayer2Grid]

        results = co.OrderedDict()
        aimActionListPlayer1 = list()
        aimActionListPlayer2 = list()

        stepCount = 0
        goalListPlayer1 = list()
        goalListPlayer2 = list()
        ifnoisePlayer1 = 0
        ifnoisePlayer2 = 0

        noiseStepPlayer1 = None
        noiseStepPlayer2 = None

        ifModifedConditionPlayer1 = False
        ifModifedConditionPlayer2 = False

        firstIntentionFlagPlayer1 = False
        firstIntentionFlagPlayer2 = False

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realGridPlayer1 = initialPlayer1Grid
        realGridPlayer2 = initialPlayer2Grid

        pause = True

        while pause:
            initialTime = time.get_ticks()
            aimPlayer1Grid, aimActionPlayer1, aimPlayer2Grid, aimActionPlayer2 = self.controller(realGridPlayer1, realGridPlayer2, bean1Grid, bean2Grid, AIPolicy)
            reactionTime.append(time.get_ticks() - initialTime)
            aimActionListPlayer1.append(aimActionPlayer1)
            aimActionListPlayer2.append(aimActionPlayer2)
            stepCount = stepCount + 1

            currentGridPlayer1 = trajectoryPlayer1[-1]
            currentGridPlayer2 = trajectoryPlayer2[-1]
            goalPlayer1 = inferGoal(currentGridPlayer1, aimPlayer1Grid, bean1Grid, bean2Grid)
            goalPlayer2 = inferGoal(currentGridPlayer2, aimPlayer2Grid, bean1Grid, bean2Grid)
            goalListPlayer1.append(goalPlayer1)
            goalListPlayer2.append(goalPlayer2)

            ### Player1
            conditionCountPlayer1 = designValuesRemainPlayer1.count('forceCommit')
            if conditionCountPlayer1 != 0 and sum(goalListPlayer1) == 0 and stepCount >= 3: # if no intention revealed in n steps
                noiseTypePlayer1 = "forceCommit"
                ifModifedConditionPlayer1 = True

            #
            if noiseTypePlayer1 == "pushForward":
                noiseGridPlayer1, firstIntentionFlagPlayer1, realActionPlayer1, noiseStepPlayer1 = self.pushForwardNoise(stepCount, currentGridPlayer1, bean1Grid, bean2Grid, aimActionPlayer1, goalPlayer1, firstIntentionFlagPlayer1)

            elif noiseTypePlayer1 == "pullBack":
                noiseGridPlayer1, firstIntentionFlagPlayer1, realActionPlayer1, noiseStepPlayer1 = self.pullBackNoise(stepCount, currentGridPlayer1, bean1Grid, bean2Grid, aimActionPlayer1, goalPlayer1, firstIntentionFlagPlayer1)

            elif noiseTypePlayer1 == "forceCommit":
                noiseGridPlayer1, firstIntentionFlagPlayer1, realActionPlayer1, noiseStepPlayer1 = self.forceToCommitNoise(stepCount, currentGridPlayer1, bean1Grid, bean2Grid, aimActionPlayer1, goalListPlayer1, firstIntentionFlagPlayer1)

            elif noiseTypePlayer1 == "noNoise":
                noiseGridPlayer1 = aimPlayer1Grid

            ### Player2
            conditionCountPlayer2 = designValuesRemainPlayer2.count('forceCommit')
            if conditionCountPlayer2 != 0 and sum(goalListPlayer2) == 0 and stepCount >= 3: # if no intention revealed in n steps
                noiseTypePlayer2 = "forceCommit"
                ifModifedConditionPlayer2 = True

            #
            if noiseTypePlayer2 == "pushForward":
                noiseGridPlayer2, firstIntentionFlagPlayer2, realActionPlayer2, noiseStepPlayer2 = self.pushForwardNoise(stepCount, currentGridPlayer2, bean1Grid, bean2Grid, aimActionPlayer2, goalPlayer2, firstIntentionFlagPlayer2)

            elif noiseTypePlayer2 == "pullBack":
                noiseGridPlayer2, firstIntentionFlagPlayer2, realActionPlayer2, noiseStepPlayer2 = self.pullBackNoise(stepCount, currentGridPlayer2, bean1Grid, bean2Grid, aimActionPlayer2, goalPlayer2, firstIntentionFlagPlayer2)

            elif noiseTypePlayer2 == "forceCommit":
                noiseGridPlayer2, firstIntentionFlagPlayer2, realActionPlayer2, noiseStepPlayer2 = self.forceToCommitNoise(stepCount, currentGridPlayer2, bean1Grid, bean2Grid, aimActionPlayer2, goalListPlayer2, firstIntentionFlagPlayer2)

            elif noiseTypePlayer2 == "noNoise":
                noiseGridPlayer2 = aimPlayer2Grid

            ###
            realGridPlayer1 = self.checkBoundary(noiseGridPlayer1)
            realGridPlayer2 = self.checkBoundary(noiseGridPlayer2)

            self.drawNewState(bean1Grid, bean2Grid, realGridPlayer1, realGridPlayer2, ifnoisePlayer1, ifnoisePlayer2)

            trajectoryPlayer1.append(tuple(realGridPlayer1))
            trajectoryPlayer2.append(tuple(realGridPlayer2))

            pause = checkTerminationOfTrial2P2G(bean1Grid, bean2Grid, realGridPlayer1, realGridPlayer2)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["reactionTime"] = str(reactionTime)
        results["noiseTypePlayer1"] = noiseTypePlayer1
        results["noiseTypePlayer2"] = noiseTypePlayer2
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        results["noisePointPlayer1"] = str(noiseStepPlayer1)
        results["noisePointPlayer2"] = str(noiseStepPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["goalPlayer2"] = str(goalListPlayer2)
        return results, noiseTypePlayer1, noiseTypePlayer2, ifModifedConditionPlayer1, ifModifedConditionPlayer2


def checkTerminationOfPracTrial(bean1Grid, humanGrid):
    if (np.linalg.norm(np.array(humanGrid) - np.array(bean1Grid), ord=1)) == 0:
        pause = False
    else:
        pause = True
    return pause

class PracTrial():
    def __init__(self, controller, drawNewState, drawText, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.checkBoundary = checkBoundary

    def __call__(self, player1Grid, bean1Grid):
        initialPlayer1Grid = player1Grid

        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionListPlayer1 = list()
        trajectoryPlayer1 = [initialPlayer1Grid]

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, initialPlayer1Grid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid

        pause = True
        while pause:
            initialTime = time.get_ticks()
            aimPlayer1Grid, aimAction = self.controller(realPlayer1Grid)
            reactionTime.append(time.get_ticks() - initialTime)

            aimActionListPlayer1.append(aimAction)
            stepCount = stepCount + 1
            realPlayer1Grid = self.checkBoundary(aimPlayer1Grid)
            self.drawNewState(bean1Grid, realPlayer1Grid)
            trajectoryPlayer1.append(list(realPlayer1Grid))
            pause = checkTerminationOfPracTrial(bean1Grid, realPlayer1Grid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["bean1GridX"] = bean1Grid[0]
        results["bean1GridY"] = bean1Grid[1]
        results["player1GridX"] = initialPlayer1Grid[0]
        results["player1GridY"] = initialPlayer1Grid[1]
        results["reactionTime"] = str(reactionTime)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        return results



class PracTrialFreePlay():
    def __init__(self, normalNoise, controller, drawNewState, drawText, checkBoundary, playTime):
        self.normalNoise = normalNoise
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.checkBoundary = checkBoundary
        self.playTime = playTime


    def __call__(self, player1Grid, bean1Grid):
        initialPlayer1Grid = player1Grid

        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionListPlayer1 = list()
        trajectoryPlayer1 = [initialPlayer1Grid]

        # self.drawText("+", [0, 0, 0], [7, 7])
        # pg.time.wait(1300)
        self.drawNewState([], initialPlayer1Grid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayerGrid = initialPlayer1Grid
        trajectory = []

        noiseSteps = [random.randint(i-10, i-1) for i in range(10, 201, 10)]
        initialTime = time.get_ticks()
        while time.get_ticks() - initialTime < self.playTime:

            aimPlayer1Grid, aimAction = self.controller(realPlayerGrid)
            noisePlayerGrid, aimAction, ifnoise = self.normalNoise(realPlayerGrid, aimAction, trajectory, noiseSteps, stepCount)

            realPlayerGrid = self.checkBoundary(noisePlayerGrid)
            reactionTime.append(time.get_ticks() - initialTime)
            aimActionListPlayer1.append(aimAction)
            stepCount = stepCount + 1
            self.drawNewState([], realPlayerGrid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["bean1GridX"] = bean1Grid[0]
        results["bean1GridY"] = bean1Grid[1]
        results["player1GridX"] = initialPlayer1Grid[0]
        results["player1GridY"] = initialPlayer1Grid[1]
        results["reactionTime"] = str(reactionTime)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        return results
