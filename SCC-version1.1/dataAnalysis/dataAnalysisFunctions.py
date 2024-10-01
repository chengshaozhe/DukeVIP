import numpy as np
from scipy.interpolate import interp1d


def calculateSD(data):
    standardD = np.std(data, ddof=1)
    return standardD

def calculateSE(data):
    standardError = np.std(data, ddof=1) / np.sqrt(len(data) - 1)
    return standardError

def calculateGridDis(grid1, grid2):
    gridDis = np.linalg.norm(np.array(grid1) - np.array(grid2), ord=1)
    return gridDis

def calStepPerformace(trajectory):
    trajectory = list(map(tuple, trajectory))
    usedSteps = len(trajectory) - 1
    minStep = calculateGridDis(trajectory[0],trajectory[-1])
    return usedSteps - minStep

def calculateFirstIntention(goalList):
    for goal in goalList:
        if goal != 0:
            firstGoal = goal
            break
        else:
            firstGoal = None
    return firstGoal

def calculateFirstIntentionConsistency(goalList):
    firstGoal = calculateFirstIntention(goalList)
    finalGoal = calculateFirstIntention(list(reversed(goalList)))
    firstIntention = 1 if firstGoal == finalGoal else 0
    return firstIntention

def isReachDiffGoal(goalPlayer1List, goalPlayer2List):
    goalPlayer1 = calculateFirstIntention(goalPlayer1List[::-1])
    goalPlayer2 = calculateFirstIntention(goalPlayer2List[::-1])
    if goalPlayer1 != goalPlayer2:
        return True
    else:
        return False

def calculateFirstIntentionStep(goalList):
    goal1Step = goal2Step = len(goalList)
    if 1 in goalList:
        goal1Step = goalList.index(1) + 1
    if 2 in goalList:
        goal2Step = goalList.index(2) + 1
    firstIntentionStep = min(goal1Step, goal2Step)
    return firstIntentionStep

def calIntentionRevealStage(firstIntentionStepHuman,firstIntentionStepMDP):
    if firstIntentionStepHuman == firstIntentionStepMDP:
        return "same"
    elif firstIntentionStepHuman < firstIntentionStepMDP:
        return "humanFirst"
    else:
        return "MDPFirst"

def calFirstRevealingStepByPosition(trajectory, goals):
    trajectory = list(map(tuple, trajectory))
    target1, target2 = goals
    for index, state in enumerate(trajectory):
        diff = abs(calculateGridDis(state,target1)-calculateGridDis(state,target2))
        if diff != 0:
            return index
            break

