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

def extractNoRepeatingElements(list, number):
    point = random.sample(list, number)
    return point


def checkTerminationOfTrial(bean1Grid, bean2Grid, humanGrid, humanGrid2):
    if (np.linalg.norm(np.array(humanGrid) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid) - np.array(bean2Grid), ord=1) == 0) and \
            (np.linalg.norm(np.array(humanGrid2) - np.array(bean1Grid), ord=1) == 0 or np.linalg.norm(np.array(humanGrid2) - np.array(bean2Grid), ord=1) == 0):
        pause = False
    else:
        pause = True
    return pause

def transition(playerPosition, action):
    newPlayerGrid = tuple(np.add(playerPosition, action))
    return newPlayerGrid

class NormalTrialSyn():
    def __init__(self, controller, drawNewState, drawText, normalNoise, checkBoundary, keyPressInterval):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.normalNoise = normalNoise
        self.checkBoundary = checkBoundary
        self.keyPressInterval = keyPressInterval

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid, designValuesPlayer1, designValuesPlayer2):
        results = co.OrderedDict()

        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

        trajectoryPlayer1 = [initialPlayer1Grid]
        trajectoryPlayer2 = [initialPlayer2Grid]
        reactionTime1 = list()
        reactionTime2 = list()
        aimActionListPlayer1 = list()
        aimActionListPlayer2 = list()
        realActionListPlayer1 = list()
        realActionListPlayer2 = list()
        goalListPlayer1 = list()
        goalListPlayer2 = list()
        noiseStepPlayer1 = list()
        noiseStepPlayer2 = list()

        actorIndexList = list()

        stepCount1 = 0
        stepCount2 = 0
        ifnoisePlayer1 = 0
        ifnoisePlayer2 = 0

        totalStep = int(np.linalg.norm(np.array(player1Grid) - np.array(bean1Grid), ord=1))
        noiseStepPlayer1 = random.sample(list(range(1, totalStep + 1)), designValuesPlayer1)
        noiseStepPlayer2 = random.sample(list(range(1, totalStep + 1)), designValuesPlayer2)

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid

        pause = True
        actor1Press = True
        actor2Press = True

        reactionTimeAll = []
        initialTime = time.get_ticks()
        while pause:
            if calculateGridDis(realPlayer1Grid, bean1Grid) == 0 or calculateGridDis(realPlayer1Grid, bean2Grid) == 0:
                actor1Press = False

            if calculateGridDis(realPlayer2Grid, bean1Grid) == 0 or calculateGridDis(realPlayer2Grid, bean2Grid) == 0:
                actor2Press = False

            aimAction, actorIndex = self.controller(bean1Grid, bean2Grid, actor1Press, actor2Press)
            rt = time.get_ticks() - initialTime

            # if len(reactionTimeAll) > 0:
            #     rt = time.get_ticks()- reactionTimeAll[-1]
            # else:
            #     rt = time.get_ticks() - initialTime

            # reactionTimeAll.append(rt)
            # print(reactionTimeAll)

            if actorIndex == 0:
                # if len(reactionTime1) > 0:
                #     if rt - reactionTime1[-1] < self.keyPressInterval:
                #         continue
                reactionTime1.append(rt)

                aimPlayer1Grid = transition(realPlayer1Grid, aimAction)
                aimActionListPlayer1.append(aimAction)

                goalPlayer1 = inferGoal(trajectoryPlayer1[-1], aimPlayer1Grid, bean1Grid, bean2Grid)
                goalListPlayer1.append(goalPlayer1)

                stepCount1 = stepCount1 + 1
                noisePlayer1Grid, realAction1, ifnoisePlayer1 = self.normalNoise(trajectoryPlayer1[-1], aimAction, trajectoryPlayer1, noiseStepPlayer1, stepCount1)
                realPlayer1Grid = self.checkBoundary(noisePlayer1Grid)
                trajectoryPlayer1.append(list(realPlayer1Grid))
                realActionListPlayer1.append(realAction1)

                player2Grid = realPlayer2Grid

            elif actorIndex == 1:
                # if len(reactionTime2) > 0:
                    # if rt - reactionTime2[-1] < self.keyPressInterval:
                    #     continue
                reactionTime2.append(rt)

                aimPlayer2Grid = transition(realPlayer2Grid, aimAction)
                aimActionListPlayer2.append(aimAction)

                goalPlayer2 = inferGoal(trajectoryPlayer2[-1], aimPlayer2Grid, bean1Grid, bean2Grid)
                goalListPlayer2.append(goalPlayer2)

                stepCount2 = stepCount2 + 1
                noisePlayer2Grid, realAction2, ifnoisePlayer2 = self.normalNoise(trajectoryPlayer2[-1], aimAction, trajectoryPlayer2, noiseStepPlayer2, stepCount2)

                realPlayer2Grid = self.checkBoundary(noisePlayer2Grid)
                trajectoryPlayer2.append(list(realPlayer2Grid))
                realActionListPlayer2.append(realAction2)
                player1Grid = realPlayer1Grid

            actorIndexList.append(actorIndex)
            self.drawNewState(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])

        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["player1reactionTime"] = str(reactionTime1)
        results["realActionPlayer1"] = str(realActionListPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["noisePointPlayer1"] = str(noiseStepPlayer1)

        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["player2reactionTime"] = str(reactionTime2)
        results["realActionPlayer2"] = str(realActionListPlayer2)
        results["goalPlayer2"] = str(goalListPlayer2)
        results["noisePointPlayer2"] = str(noiseStepPlayer2)

        results["actorIndexList"] = str(actorIndexList)

        return results


class SpecialTrialSyn():
    def __init__(self, controller, drawNewState, drawText, awayFromTheGoalNoise, checkBoundary, keyPressInterval):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawText = drawText
        self.awayFromTheGoalNoise = awayFromTheGoalNoise
        self.checkBoundary = checkBoundary
        self.keyPressInterval = keyPressInterval

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid, designValuesPlayer1, designValuesPlayer2):
        results = co.OrderedDict()

        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

        trajectoryPlayer1 = [initialPlayer1Grid]
        trajectoryPlayer2 = [initialPlayer2Grid]
        reactionTime1 = list()
        reactionTime2 = list()
        aimActionListPlayer1 = list()
        aimActionListPlayer2 = list()
        realActionListPlayer1 = list()
        realActionListPlayer2 = list()
        goalListPlayer1 = list()
        goalListPlayer2 = list()
        noiseStepPlayer1 = list()
        noiseStepPlayer2 = list()

        actorIndexList = list()

        stepCount1 = 0
        stepCount2 = 0
        ifnoisePlayer1 = 0
        ifnoisePlayer2 = 0

        firstIntentionFlag = False
        firstIntentionFlag2 = False

        self.drawText("+", [0, 0, 0], [7, 7])
        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid

        pause = True
        actor1Press = True
        actor2Press = True

        initialTime = time.get_ticks()
        while pause:
            if calculateGridDis(realPlayer1Grid, bean1Grid) == 0 or calculateGridDis(realPlayer1Grid, bean2Grid) == 0:
                actor1Press = False

            if calculateGridDis(realPlayer2Grid, bean1Grid) == 0 or calculateGridDis(realPlayer2Grid, bean2Grid) == 0:
                actor2Press = False

            aimAction, actorIndex = self.controller(bean1Grid, bean2Grid, actor1Press, actor2Press)
            rt = time.get_ticks() - initialTime


            if actorIndex == 0:
                if len(reactionTime1) > 0:
                    if rt - reactionTime1[-1] < self.keyPressInterval:
                        continue
                reactionTime1.append(rt)

                aimPlayer1Grid = transition(realPlayer1Grid, aimAction)
                aimActionListPlayer1.append(aimAction)

                goalPlayer1 = inferGoal(trajectoryPlayer1[-1], aimPlayer1Grid, bean1Grid, bean2Grid)
                goalListPlayer1.append(goalPlayer1)

                stepCount1 = stepCount1 + 1

                noisePlayer1Grid, firstIntentionFlag, noiseStepPlayer1, realActionPlayer1, ifnoisePlayer1 = self.awayFromTheGoalNoise(trajectoryPlayer1[-1], bean1Grid, bean2Grid, aimAction, goalPlayer1, firstIntentionFlag,stepCount1)

                realPlayer1Grid = self.checkBoundary(noisePlayer1Grid)
                trajectoryPlayer1.append(list(realPlayer1Grid))
                realActionListPlayer1.append(realActionPlayer1)

                player2Grid = realPlayer2Grid

            elif actorIndex == 1:
                if len(reactionTime2) > 0:
                    if rt - reactionTime2[-1] < self.keyPressInterval:
                        continue
                reactionTime2.append(rt)

                aimPlayer2Grid = transition(realPlayer2Grid, aimAction)
                aimActionListPlayer2.append(aimAction)

                goalPlayer2 = inferGoal(trajectoryPlayer2[-1], aimPlayer2Grid, bean1Grid, bean2Grid)
                goalListPlayer2.append(goalPlayer2)

                stepCount2 = stepCount2 + 1
                noisePlayer2Grid, firstIntentionFlag2, noiseStepPlayer2, realActionPlayer2, ifnoisePlayer2 = self.awayFromTheGoalNoise(
                    trajectoryPlayer2[-1], bean1Grid, bean2Grid, aimAction, goalPlayer2, firstIntentionFlag2, stepCount2)

                realPlayer2Grid = self.checkBoundary(noisePlayer2Grid)

                trajectoryPlayer2.append(list(realPlayer2Grid))
                realActionListPlayer2.append(realActionPlayer2)
                player1Grid = realPlayer1Grid

            actorIndexList.append(actorIndex)
            self.drawNewState(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])

        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["player1reactionTime"] = str(reactionTime1)
        results["realActionPlayer1"] = str(realActionListPlayer1)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["noisePointPlayer1"] = str(noiseStepPlayer1)

        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["player2reactionTime"] = str(reactionTime2)
        results["realActionPlayer2"] = str(realActionListPlayer2)
        results["goalPlayer2"] = str(goalListPlayer2)
        results["noisePointPlayer2"] = str(noiseStepPlayer2)

        results["actorIndexList"] = str(actorIndexList)

        return results