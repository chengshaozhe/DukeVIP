import numpy as np
import pygame as pg
import random



class NormalNoise():
    def __init__(self, controller):
        self.actionSpace = controller.actionSpace
        self.gridSize = controller.gridSize

    def __call__(self, playerGrid, action, trajectory, noiseStep, stepCount):
        ifnoise = 0
        if action != (0,0):
            if stepCount in noiseStep:
                actionSpace = self.actionSpace.copy()
                actionSpace.remove(action)
                actionList = [str(action) for action in actionSpace]
                actionStr = np.random.choice(actionList)
                realAction = eval(actionStr)
                ifnoise = 1
            else:
                realAction = action

        else:
            realAction = action
        realPlayerGrid = tuple(np.add(playerGrid, realAction))
        return realPlayerGrid, realAction, ifnoise

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

def selectActionMinDistanceFromTarget(goal, playerGrid, bean1Grid, bean2Grid, actionSpace):
    allPosiibilePlayerGrid = [np.add(playerGrid, action) for action in actionSpace]
    allActionGoal = [inferGoal(playerGrid, possibleGrid, bean1Grid, bean2Grid) for possibleGrid in
                     allPosiibilePlayerGrid]
    if goal == 1:
        realActionIndex = allActionGoal.index(2)
    else:
        realActionIndex = allActionGoal.index(1)
    realAction = actionSpace[realActionIndex]
    return realAction


class AwayFromTheGoalNoise():
    def __init__(self, controller):
        self.actionSpace = controller.actionSpace
        self.gridSize = controller.gridSize

    def __call__(self, playerGrid, bean1Grid, bean2Grid, action, goal, firstIntentionFlag, stepCount):
        ifnoise = 0
        noiseStep = 0
        if goal != 0 and not firstIntentionFlag:
            noiseStep = [stepCount]
            firstIntentionFlag = True
            realAction = selectActionMinDistanceFromTarget(goal, playerGrid, bean1Grid, bean2Grid, self.actionSpace)
            ifnoise = 1
        else:
            realAction = action
        realPlayerGrid = tuple(np.add(playerGrid, realAction))
        return realPlayerGrid, firstIntentionFlag, noiseStep, realAction, ifnoise


class HumanControllerNoUpdate():
    def __init__(self, gridSize):
        self.actionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
        self.actionDict2 = {pg.K_w: (0, -1), pg.K_s: (0, 1), pg.K_a: (-1, 0), pg.K_d: (1, 0)}
        self.actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.gridSize = gridSize

    def __call__(self, targetPositionA, targetPositionB, actor1Press, actor2Press):
        action = [0, 0]
        pause = True
        while pause:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if actor1Press:
                        if event.key in self.actionDict.keys():
                            action = self.actionDict[event.key]
                            index = 0
                            pause = False
                        elif event.key == pg.K_ESCAPE:
                            pg.quit()
                            exit()
                    if actor2Press:
                        if event.key in self.actionDict2.keys():
                            action = self.actionDict2[event.key]
                            index = 1
                            pause = False
                        elif event.key == pg.K_ESCAPE:
                            pg.quit()
                            exit()
        return action, index

class CheckBoundary():
    def __init__(self, xBoundary, yBoundary):
        self.xMin, self.xMax = xBoundary
        self.yMin, self.yMax = yBoundary

    def __call__(self, position):
        adjustedX, adjustedY = position
        if position[0] >= self.xMax:
            adjustedX = self.xMax
        if position[0] <= self.xMin:
            adjustedX = self.xMin
        if position[1] >= self.yMax:
            adjustedY = self.yMax
        if position[1] <= self.yMin:
            adjustedY = self.yMin
        checkedPosition = (adjustedX, adjustedY)
        return checkedPosition



