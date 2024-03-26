import numpy as np
import pygame as pg
from pygame import time
import collections as co
import pickle
import random

def inferGoal(originGrid, aimGrid, targetGridA, targetGridB):
    pacmanBean1aimDisplacement = np.linalg.norm(np.array(targetGridA) - np.array(aimGrid), ord=1)
    pacmanBean2aimDisplacement = np.linalg.norm(np.array(targetGridB) - np.array(aimGrid), ord=1)
    pacmanBean1LastStepDisplacement = np.linalg.norm(np.array(targetGridA) - np.array(originGrid), ord=1)
    pacmanBean2LastStepDisplacement = np.linalg.norm(np.array(targetGridB) - np.array(originGrid), ord=1)
    bean1Goal = pacmanBean1LastStepDisplacement - pacmanBean1aimDisplacement
    bean2Goal = pacmanBean2LastStepDisplacement - pacmanBean2aimDisplacement
    if bean1Goal > bean2Goal:
        goal = 1
    elif bean1Goal < bean2Goal:
        goal = 2
    else:
        goal = 0
    return goal


def checkTerminationOfTrial(bean1Grid, bean2Grid, humanGrid, humanGrid2):
    if (np.linalg.norm(np.array(humanGrid) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid) - np.array(bean2Grid), ord=1) == 0) and \
            (np.linalg.norm(np.array(humanGrid2) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid2) - np.array(bean2Grid), ord=1) == 0):
        pause = False
    else:
        pause = True
    return pause


class NormalTrial():
    def __init__(self, controller, drawNewState, drawText, normalNoise, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.normalNoise = normalNoise
        self.checkBoundary = checkBoundary

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid, designValuesPlayer1, designValuesPlayer2, AIPolicy):
        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

        initialTime = time.get_ticks()
        reactionTime = list()
        trajectoryPlayer1 = [initialPlayer1Grid]
        trajectoryPlayer2 = [initialPlayer2Grid]

        results = co.OrderedDict()
        aimActionListPlayer1 = list()
        aimActionListPlayer2 = list()
        realActionListPlayer1 = list()
        realActionListPlayer2 = list()

        totalStep = int(np.linalg.norm(np.array(player1Grid) - np.array(bean1Grid), ord=1))
        noiseStepPlayer1 = random.sample(list(range(1, totalStep + 1)), designValuesPlayer1)
        noiseStepPlayer2 = random.sample(list(range(1, totalStep + 1)), designValuesPlayer2)

        stepCount = 0
        goalListPlayer1 = list()
        goalListPlayer2 = list()
        ifnoisePlayer1 = 0
        ifnoisePlayer2 = 0

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid

        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pause = True

        while pause:
            initialTime = time.get_ticks()
            aimPlayer1Grid, aimAction, aimPlayer2Grid, aimAction2 = self.controller(realPlayer1Grid, realPlayer2Grid, bean1Grid, bean2Grid, AIPolicy)
            reactionTime.append(time.get_ticks() - initialTime)

            goalPlayer1 = inferGoal(trajectoryPlayer1[-1], aimPlayer1Grid, bean1Grid, bean2Grid)
            goalPlayer2 = inferGoal(trajectoryPlayer2[-1], aimPlayer2Grid, bean1Grid, bean2Grid)
            goalListPlayer1.append(goalPlayer1)
            goalListPlayer2.append(goalPlayer2)
            aimActionListPlayer1.append(aimAction)
            aimActionListPlayer2.append(aimAction2)

            stepCount = stepCount + 1
            noisePlayer1Grid, realAction, ifnoisePlayer1 = self.normalNoise(trajectoryPlayer1[-1], aimAction, trajectoryPlayer1, noiseStepPlayer1, stepCount)
            noisePlayer2Grid, realAction2, ifnoisePlayer2 = self.normalNoise(trajectoryPlayer2[-1], aimAction2, trajectoryPlayer2, noiseStepPlayer2, stepCount)

            realPlayer1Grid = self.checkBoundary(noisePlayer1Grid)
            realPlayer2Grid = self.checkBoundary(noisePlayer2Grid)
            self.drawNewState(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
            trajectoryPlayer1.append(list(realPlayer1Grid))
            trajectoryPlayer2.append(list(realPlayer2Grid))
            realActionListPlayer1.append(realAction)
            realActionListPlayer2.append(realAction2)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["bean1GridX"] = bean1Grid[0]
        results["bean1GridY"] = bean1Grid[1]
        results["bean2GridX"] = bean2Grid[0]
        results["bean2GridY"] = bean2Grid[1]
        results["player1GridX"] = initialPlayer1Grid[0]
        results["player1GridY"] = initialPlayer1Grid[1]
        results["player2GridX"] = initialPlayer2Grid[0]
        results["player2GridY"] = initialPlayer2Grid[1]
        results["reactionTime"] = str(reactionTime)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["realActionPlayer1"] = str(aimActionListPlayer1)
        results["realActionPlayer2"] = str(aimActionListPlayer2)
        results["noisePointPlayer1"] = str(noiseStepPlayer1)
        results["noisePointPlayer2"] = str(noiseStepPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["goalPlayer2"] = str(goalListPlayer2)
        return results


class SpecialTrial():
    def __init__(self, controller, drawNewState, drawText, awayFromTheGoalNoise, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.awayFromTheGoalNoise = awayFromTheGoalNoise
        self.checkBoundary = checkBoundary

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid,  designValuesPlayer1, designValuesPlayer2,AIPolicy):
        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

        initialTime = time.get_ticks()
        reactionTime = list()
        trajectoryPlayer1 = [initialPlayer1Grid]
        trajectoryPlayer2 = [initialPlayer2Grid]

        results = co.OrderedDict()
        aimActionListPlayer1 = list()
        aimActionListPlayer2 = list()
        realActionListPlayer1 = list()
        realActionListPlayer2 = list()

        firstIntentionFlag = False
        firstIntentionFlag2 = False
        noiseStepPlayer1 = list()
        noiseStepPlayer2 = list()
        stepCount = 0
        goalListPlayer1 = list()
        goalListPlayer2 = list()

        ifnoisePlayer1 = 0
        ifnoisePlayer2 = 0
        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid
        pause = True
        while pause:
            initialTime = time.get_ticks()
            aimPlayer1Grid, aimAction,  aimPlayer2Grid, aimAction2 = self.controller(realPlayer1Grid, realPlayer2Grid, bean1Grid, bean2Grid, AIPolicy)
            reactionTime.append(time.get_ticks() - initialTime)

            goalPlayer1 = inferGoal(trajectoryPlayer1[-1], aimPlayer1Grid, bean1Grid, bean2Grid)
            goalPlayer2 = inferGoal(trajectoryPlayer2[-1], aimPlayer2Grid, bean1Grid, bean2Grid)
            goalListPlayer1.append(goalPlayer1)
            goalListPlayer2.append(goalPlayer2)

            stepCount = stepCount + 1
            noisePlayer1Grid, firstIntentionFlag, noiseStepPlayer1, realActionPlayer1, ifnoisePlayer1 = self.awayFromTheGoalNoise(
                trajectoryPlayer1[-1], bean1Grid, bean2Grid, aimAction, goalPlayer1, firstIntentionFlag, noiseStepPlayer1, stepCount)
            noisePlayer2Grid, firstIntentionFlag2, noiseStepPlayer2, realActionPlayer2, ifnoisePlayer2 = self.awayFromTheGoalNoise(
                trajectoryPlayer2[-1], bean1Grid, bean2Grid, aimAction2, goalPlayer2, firstIntentionFlag2, noiseStepPlayer2, stepCount)

            realPlayer1Grid = self.checkBoundary(noisePlayer1Grid)
            realPlayer2Grid = self.checkBoundary(noisePlayer2Grid)
            self.drawNewState(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
            trajectoryPlayer1.append(list(realPlayer1Grid))
            trajectoryPlayer2.append(list(realPlayer2Grid))
            aimActionListPlayer1.append(aimAction)
            aimActionListPlayer2.append(aimAction)
            realActionListPlayer1.append(realActionPlayer1)
            realActionListPlayer2.append(realActionPlayer2)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)
        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["bean1GridX"] = bean1Grid[0]
        results["bean1GridY"] = bean1Grid[1]
        results["bean2GridX"] = bean2Grid[0]
        results["bean2GridY"] = bean2Grid[1]
        results["player1GridX"] = initialPlayer1Grid[0]
        results["player1GridY"] = initialPlayer1Grid[1]
        results["player2GridX"] = initialPlayer2Grid[0]
        results["player2GridY"] = initialPlayer2Grid[1]
        results["reactionTime"] = str(reactionTime)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["realActionPlayer1"] = str(realActionListPlayer1)
        results["realActionPlayer2"] = str(realActionListPlayer2)
        results["noisePointPlayer1"] = str(noiseStepPlayer1)
        results["noisePointPlayer2"] = str(noiseStepPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["goalPlayer2"] = str(goalListPlayer2)
        return results

