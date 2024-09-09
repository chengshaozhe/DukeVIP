import numpy as np
import pygame as pg
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


def countCertainNumberInList(listToManipulate, certainNumber):
    count = 0
    indexList = list()
    for i in range(len(listToManipulate)):
        if certainNumber == listToManipulate[i]:
            count = count + 1
            indexList.append(i)

    return count, indexList


def calculateSoftmaxProbability(acionValues, beta):
    expont = [min(700, i) for i in np.multiply(beta, acionValues)]
    newProbabilityList = list(np.divide(np.exp(expont), np.sum(np.exp(expont))))

    return newProbabilityList


class SoftmaxPolicy:
    def __init__(self, Q_dict, softmaxBeta):
        self.Q_dict = Q_dict
        self.softmaxBeta = softmaxBeta

    def __call__(self, playerGrid, target1):
        actionDict = self.Q_dict[(playerGrid, target1)]
        actionValues = list(actionDict.values())
        softmaxProbabilityList = calculateSoftmaxProbability(actionValues, self.softmaxBeta)
        softMaxActionDict = dict(zip(actionDict.keys(), softmaxProbabilityList))
        return softMaxActionDict


class NormalNoise():
    def __init__(self, controller):
        self.actionSpace = controller.actionSpace

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

    def __call__(self, playerGrid, bean1Grid, bean2Grid, action, goal, firstIntentionFlag, noiseStep, stepCount):
        ifnoise = 0
        if goal != 0 and not firstIntentionFlag:
            noiseStep.append(stepCount)
            firstIntentionFlag = True
            realAction = selectActionMinDistanceFromTarget(goal, playerGrid, bean1Grid, bean2Grid, self.actionSpace)
            ifnoise = 1
        else:
            realAction = action
        realPlayerGrid = tuple(np.add(playerGrid, realAction))
        return realPlayerGrid, firstIntentionFlag, noiseStep, realAction, ifnoise

class SingleController():
    def __init__(self, keyBoradActionDict):
        self.keyBoradActionDict = keyBoradActionDict
        self.actionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
        self.actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def __call__(self, playerGrid):
        action = [0, 0]
        pause = True
        while pause:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                if event.type == pg.KEYDOWN:
                    if event.key in self.keyBoradActionDict.keys():
                        action = self.keyBoradActionDict[event.key]
                        aimePlayerGrid = tuple(np.add(playerGrid, action))
                        pause = False
        return aimePlayerGrid, action

class Controller():
    def __init__(self, gridSize, softmaxBeta):
        self.actionDict = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
        self.actionSpace = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.gridSize = gridSize
        self.softmaxBeta = softmaxBeta

    def __call__(self, player1Grid, player2Grid, targetGrid1, targetGrid2, AIPolicy):
        action1 = [0, 0]
        action2 = [0, 0]
        pause = True
        while pause:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                if event.type == pg.KEYDOWN:
                    if event.key in self.actionDict.keys():
                        action1 = self.actionDict[event.key]
                        aimePlayer1Grid = tuple(np.add(player1Grid, action1))
                        pause = False
            if player1Grid in [targetGrid1, targetGrid2]:
                pause = False
                aimePlayer1Grid = player1Grid
                action1 = (0,0)
                pg.time.wait(np.random.randint(250,350))

        QDict = AIPolicy[player2Grid]
        action2 = chooseSoftMaxAction(QDict, self.softmaxBeta)
        # action2 = chooseMaxAcion(QDict)
        aimePlayer2Grid = transition(player2Grid, action2)

        if player2Grid in [targetGrid1, targetGrid2]:
            action2 = (0,0)
            aimePlayer2Grid = player2Grid
        return aimePlayer1Grid, action1, aimePlayer2Grid, action2

def transition(state,action):
    nextState = tuple(np.add(state, action))
    return nextState

def chooseMaxAcion(actionDict):
    actionMaxList = [action for action in actionDict.keys() if
                     actionDict[action] == np.max(list(actionDict.values()))]
    action = random.choice(actionMaxList)
    return action


def chooseSoftMaxAction(actionDict, softmaxBeta):
    actionValue = list(actionDict.values())
    softmaxProbabilityList = calculateSoftmaxProbability(actionValue, softmaxBeta)
    action = list(actionDict.keys())[
        list(np.random.multinomial(1, softmaxProbabilityList)).index(1)]
    return action


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


