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

def checkTerminationOfTrialSameBean(bean1Grid, bean2Grid, humanGrid, humanGrid2):
    disToTargetA1 = calculateGridDis(humanGrid, bean1Grid)
    disToTargetA2 = calculateGridDis(humanGrid2, bean1Grid)
    disToTargetB1 = calculateGridDis(humanGrid, bean2Grid)
    disToTargetB2 = calculateGridDis(humanGrid2, bean2Grid)

    if (disToTargetA1 == 0 and disToTargetA2 == 0) or (disToTargetB1 == 0 and disToTargetB2 == 0):
        pause = False
    else:
        pause = True
    return pause

def checkTerminationOfTrialDifferentBean(bean1Grid, bean2Grid, humanGrid, humanGrid2):
    disToTargetA1 = calculateGridDis(humanGrid, bean1Grid)
    disToTargetA2 = calculateGridDis(humanGrid2, bean1Grid)
    disToTargetB1 = calculateGridDis(humanGrid, bean2Grid)
    disToTargetB2 = calculateGridDis(humanGrid2, bean2Grid)

    if (disToTargetA1 == 0 and disToTargetB2 == 0) or (disToTargetB1 == 0 and disToTargetA2 == 0):
        pause = False
    else:
        pause = True
    return pause


class NormalTrial1P2G():
    def __init__(self, controller, drawNewState, drawFixation, normalNoise, checkBoundary, saveImageDir=None):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.normalNoise = normalNoise
        self.checkBoundary = checkBoundary
        self.saveImageDir = saveImageDir

    def __call__(self, bean1Grid, bean2Grid, playerGrid, designValues):
        stepCount = 0
        reactionTime = list()
        aimActionList = list()
        goalList = list()
        results = co.OrderedDict()

        initialPlayerGrid = playerGrid
        trajectory = [initialPlayerGrid]

        totalSteps = int(np.linalg.norm(np.array(playerGrid) - np.array(bean1Grid), ord=1))
        noiseStep = random.sample(list(range(1, totalSteps + 1)), designValues)

        self.drawFixation()
        pg.time.wait(1300)
        screen = self.drawNewState(bean1Grid, bean2Grid, initialPlayerGrid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        if self.saveImageDir:
            filenameList = os.listdir(self.saveImageDir)
            pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')

        realPlayerGrid = initialPlayerGrid

        pause = True
        while pause:
            initialTime = time.get_ticks()
            aimPlayerGrid, aimAction = self.controller(realPlayerGrid)
            reactionTime.append(time.get_ticks() - initialTime)

            stepCount = stepCount + 1
            goal = inferGoal(trajectory[-1], aimPlayerGrid, bean1Grid, bean2Grid)
            noisePlayerGrid, aimAction, ifnoise = self.normalNoise(trajectory[-1], aimAction, trajectory, noiseStep, stepCount)
            realPlayerGrid = self.checkBoundary(noisePlayerGrid)

            screen = self.drawNewState(bean1Grid, bean2Grid, realPlayerGrid)
            if self.saveImageDir:
                filenameList = os.listdir(self.saveImageDir)
                pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')

            goalList.append(goal)
            trajectory.append(tuple(realPlayerGrid))
            aimActionList.append(aimAction)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayerGrid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])

        if self.saveImageDir:
            filenameList = os.listdir(self.saveImageDir)
            pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')

        results["reactionTime"] = str(reactionTime)
        results["trajectory"] = str(trajectory)
        results["aimAction"] = str(aimActionList)
        results["noisePoint"] = str(noiseStep)
        results["goal"] = str(goalList)
        return results

class SpecialTrial1P2G():
    def __init__(self, controller, drawNewState, drawFixation, awayFromTheGoalNoise, checkBoundary, saveImageDir=None):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.awayFromTheGoalNoise = awayFromTheGoalNoise
        self.checkBoundary = checkBoundary
        self.saveImageDir = saveImageDir

    def __call__(self, bean1Grid, bean2Grid, playerGrid, designValues):
        initialPlayerGrid = playerGrid
        initialTime = time.get_ticks()
        reactionTime = list()
        trajectory = [initialPlayerGrid]
        results = co.OrderedDict()
        aimActionList = list()
        firstIntentionFlag = False
        noiseStep = list()
        stepCount = 0
        goalList = list()
        self.drawFixation()
        pg.time.wait(1300)
        screen = self.drawNewState(bean1Grid, bean2Grid, initialPlayerGrid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        if self.saveImageDir:
            filenameList = os.listdir(self.saveImageDir)
            pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')

        realPlayerGrid = initialPlayerGrid
        pause = True
        while pause:
            initialTime = time.get_ticks()
            aimPlayerGrid, aimAction = self.controller(realPlayerGrid)
            reactionTime.append(time.get_ticks() - initialTime)

            goal = inferGoal(trajectory[-1], aimPlayerGrid, bean1Grid, bean2Grid)
            stepCount = stepCount + 1

            noisePlayerGrid, firstIntentionFlag, noiseStep,realAction, ifnoise = self.awayFromTheGoalNoise(
                trajectory[-1], bean1Grid, bean2Grid, aimAction, goal, firstIntentionFlag, noiseStep, stepCount)

            realPlayerGrid = self.checkBoundary(noisePlayerGrid)

            screen = self.drawNewState(bean1Grid, bean2Grid, realPlayerGrid)
            if self.saveImageDir:
                filenameList = os.listdir(self.saveImageDir)
                pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')
            trajectory.append(tuple(realPlayerGrid))
            aimActionList.append(aimAction)
            goalList.append(goal)

            pause = checkTerminationOfTrial(bean1Grid, bean2Grid, realPlayerGrid)

        pg.time.wait(500)
        if self.saveImageDir:
            filenameList = os.listdir(self.saveImageDir)
            pg.image.save(screen, self.saveImageDir + '/' + str(len(filenameList)) + '.png')

        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["reactionTime"] = str(reactionTime)
        results["trajectory"] = str(trajectory)
        results["aimAction"] = str(aimActionList)
        results["noisePoint"] = str(noiseStep)
        results["goal"] = str(goalList)
        return results

class NormalTrialHumanAISameGoal():
    def __init__(self, controller, drawNewState, drawNewStateWithArrow, drawFixation, normalNoise, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawNewStateWithArrow = drawNewStateWithArrow
        self.drawFixation = drawFixation
        self.normalNoise = normalNoise
        self.checkBoundary = checkBoundary

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid, designValuesPlayer1, designValuesPlayer2, AIPolicy):
        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

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

        # self.drawFixation()
        self.drawFixation()

        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        # self.drawNewStateWithArrow(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid

        pause = True
        startTime = time.get_ticks()
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
            trajectoryPlayer1.append(tuple(realPlayer1Grid))
            trajectoryPlayer2.append(tuple(realPlayer2Grid))
            realActionListPlayer1.append(realAction)
            realActionListPlayer2.append(realAction2)

            # pause = checkTerminationOfTrial2P2G(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)
            pause = checkTerminationOfTrialSameBean(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)
            if time.get_ticks() - startTime >= 40 * 1000:
                font = pg.font.Font(None, 50)
                text = font.render("Moving to the next round!", True, (255, 0, 0))
                textRect = text.get_rect()
                screen = pg.display.get_surface()
                screen_width = screen.get_width()
                screen_height = screen.get_height()
                textRect.center = (screen_width//2, screen_height//2)

                # Create background rectangle
                padding = 20
                bgRect = pg.Rect(textRect.left - padding, textRect.top - padding,
                               textRect.width + 2*padding, textRect.height + 2*padding)
                pg.draw.rect(screen, (255, 255, 255), bgRect)
                pg.draw.rect(screen, (0, 0, 0), bgRect, 2)
                screen.blit(text, textRect)
                pg.display.flip()
                pg.time.wait(5000)


        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["reactionTime"] = str(reactionTime)

        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        # results["realActionPlayer1"] = str(aimActionListPlayer1)
        # results["realActionPlayer2"] = str(aimActionListPlayer2)
        # results["noisePointPlayer1"] = str(noiseStepPlayer1)
        # results["noisePointPlayer2"] = str(noiseStepPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["goalPlayer2"] = str(goalListPlayer2)
        return results

class NormalTrialHumanAIDifferentGoal():
    def __init__(self, controller, drawNewState, drawNewStateWithArrow, drawFixation, normalNoise, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawNewStateWithArrow = drawNewStateWithArrow
        self.drawFixation = drawFixation
        self.normalNoise = normalNoise
        self.checkBoundary = checkBoundary

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid, designValuesPlayer1, designValuesPlayer2, AIPolicy):
        initialPlayer1Grid = player1Grid
        initialPlayer2Grid = player2Grid

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

        # self.drawFixation()
        self.drawFixation()

        pg.time.wait(1300)
        self.drawNewState(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        # self.drawNewStateWithArrow(bean1Grid, bean2Grid, initialPlayer1Grid, initialPlayer2Grid, ifnoisePlayer1, ifnoisePlayer2)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayer1Grid = initialPlayer1Grid
        realPlayer2Grid = initialPlayer2Grid

        pause = True
        startTime = time.get_ticks()
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
            trajectoryPlayer1.append(tuple(realPlayer1Grid))
            trajectoryPlayer2.append(tuple(realPlayer2Grid))
            realActionListPlayer1.append(realAction)
            realActionListPlayer2.append(realAction2)

            pause = checkTerminationOfTrialDifferentBean(bean1Grid, bean2Grid, realPlayer1Grid, realPlayer2Grid)
            if time.get_ticks() - startTime >= 40 * 1000:
                font = pg.font.Font(None, 50)
                text = font.render("Moving to the next round!", True, (255, 0, 0))
                textRect = text.get_rect()
                screen = pg.display.get_surface()
                screen_width = screen.get_width()
                screen_height = screen.get_height()
                textRect.center = (screen_width//2, screen_height//2)

                # Create background rectangle
                padding = 20
                bgRect = pg.Rect(textRect.left - padding, textRect.top - padding,
                               textRect.width + 2*padding, textRect.height + 2*padding)
                pg.draw.rect(screen, (255, 255, 255), bgRect)
                pg.draw.rect(screen, (0, 0, 0), bgRect, 2)
                screen.blit(text, textRect)
                pg.display.flip()
                pg.time.wait(5000)

                pause = False

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        results["reactionTime"] = str(reactionTime)

        results["aimActionPlayer2"] = str(aimActionListPlayer2)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["trajectoryPlayer2"] = str(trajectoryPlayer2)
        # results["realActionPlayer1"] = str(aimActionListPlayer1)
        # results["realActionPlayer2"] = str(aimActionListPlayer2)
        # results["noisePointPlayer1"] = str(noiseStepPlayer1)
        # results["noisePointPlayer2"] = str(noiseStepPlayer2)
        results["goalPlayer1"] = str(goalListPlayer1)
        results["goalPlayer2"] = str(goalListPlayer2)
        return results



class SpecialTrialHumanAI():
    def __init__(self, controller, drawNewState, drawFixation, awayFromTheGoalNoise, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.awayFromTheGoalNoise = awayFromTheGoalNoise
        self.checkBoundary = checkBoundary

    def __call__(self, bean1Grid, bean2Grid, player1Grid, player2Grid,  designValuesPlayer1, designValuesPlayer2, AIPolicy):
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
        self.drawFixation()
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


def checkTerminationOfPracTrial(bean1Grid, humanGrid):
    if (np.linalg.norm(np.array(humanGrid) - np.array(bean1Grid), ord=1)) == 0:
        pause = False
    else:
        pause = True
    return pause

class PracTrial():
    def __init__(self, controller, drawNewState, drawFixation, checkBoundary):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.checkBoundary = checkBoundary

    def __call__(self, player1Grid, bean1Grid):
        initialPlayer1Grid = player1Grid

        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionListPlayer1 = list()
        trajectoryPlayer1 = [initialPlayer1Grid]

        self.drawFixation()
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
            trajectoryPlayer1.append(tuple(realPlayer1Grid))
            pause = checkTerminationOfPracTrial(bean1Grid, realPlayer1Grid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["beanGrid"] = str(bean1Grid)
        results["playerGrid"] = str(initialPlayer1Grid)
        results["reactionTime"] = str(reactionTime)
        results["trajectoryPlayer1"] = str(trajectoryPlayer1)
        results["aimActionPlayer1"] = str(aimActionListPlayer1)
        return results


class PracTrialFreePlayNoBumps():
    def __init__(self, controller, drawNewState, drawFixation, checkBoundary, playTime):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.checkBoundary = checkBoundary
        self.playTime = playTime


    def __call__(self, player1Grid, bean1Grid):
        initialPlayer1Grid = player1Grid

        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionListPlayer1 = list()

        self.drawNewState([], initialPlayer1Grid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayerGrid = initialPlayer1Grid
        trajectory = [initialPlayer1Grid]

        initialTime = time.get_ticks()
        while time.get_ticks() - initialTime < self.playTime:

            time0 = time.get_ticks()
            aimPlayerGrid, aimAction = self.controller(realPlayerGrid)
            reactionTime.append(time.get_ticks() - time0)

            realPlayerGrid = self.checkBoundary(aimPlayerGrid)
            trajectory.append(realPlayerGrid)
            aimActionListPlayer1.append(aimAction)
            stepCount = stepCount + 1
            self.drawNewState([], realPlayerGrid)

        pg.time.wait(500)
        pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP])
        results["playerGrid"] = str(player1Grid)
        results["reactionTime"] = str(reactionTime)
        results["trajectory"] = str(trajectory)
        results["aimActionPlayer"] = str(aimActionListPlayer1)
        return results



class PracTrialFreePlay():
    def __init__(self, normalNoise, controller, drawNewState, drawFixation, checkBoundary, playTime):
        self.normalNoise = normalNoise
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.checkBoundary = checkBoundary
        self.playTime = playTime


    def __call__(self, player1Grid, bean1Grid):
        initialPlayer1Grid = player1Grid

        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionListPlayer1 = list()
        trajectoryPlayer1 = [initialPlayer1Grid]

        # self.drawFixation()
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

class Trial2Disruptions():
    def __init__(self, controller, drawNewState, drawFixation, checkBoundary, pushForwardNoise ,pullBackNoise):
        self.controller = controller
        self.drawNewState = drawNewState
        self.drawFixation = drawFixation
        self.checkBoundary = checkBoundary
        self.pushForwardNoise = pushForwardNoise
        self.pullBackNoise = pullBackNoise

    def __call__(self, bean1Grid, bean2Grid, initPlayerGrid, noiseType, noiseDesignValuesRemained):
        results = co.OrderedDict()
        stepCount = 0
        reactionTime = list()
        aimActionList = list()
        goalList = list()
        results = co.OrderedDict()
        noiseStep = None

        trajectory = [initPlayerGrid]

        self.drawFixation()
        pg.time.wait(1000)
        self.drawNewState(bean1Grid, bean2Grid, initPlayerGrid)
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])

        realPlayerGrid = initPlayerGrid

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

            ###
            if noiseType == "pushForward":
                noisePlayerGrid, firstIntentionFlag, realAction, noiseStep = self.pushForwardNoise(stepCount, currentGrid, bean1Grid, bean2Grid, aimAction, goal, firstIntentionFlag)

            elif noiseType == "pullBack":
                noisePlayerGrid, firstIntentionFlag, realAction, noiseStep = self.pullBackNoise(stepCount, currentGrid, bean1Grid, bean2Grid, aimAction, goal, firstIntentionFlag)

            elif noiseType == "noNoise":
                noisePlayerGrid = aimPlayerGrid

            realPlayerGrid = self.checkBoundary(noisePlayerGrid)


            realPlayerGrid = [int(realPlayerGrid[0]),int(realPlayerGrid[1])]
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

        return results, noiseType

