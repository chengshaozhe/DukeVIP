import numpy as np
import collections as co
import functools as ft
import itertools as it
import operator as op
import matplotlib.pyplot as plt


def signod_barrier(x, c=0, m=1, s=1):
    expt_term = np.exp(-s * (x - c))
    result = m / (1.0 + expt_term)
    return result


def barrier_feature(s, bound=0, dim=0, sign=1, barrier_func=None):
    s_arr = np.asarray(s)
    x = (s_arr[:, dim] - bound) * sign
    return -barrier_func(x)


def barrier_punish(s, a, barrier_func=None, upper=None, lower=None):
    sn_arr = np.asarray(s)
    to_upper = sn_arr - upper
    to_lower = lower - sn_arr
    punishment = barrier_func(np.hstack([to_upper, to_lower]))
    return -1 * np.sum(punishment, axis=-1)


def l2_norm(s0, s1, rho=1):
    diff = (np.asarray(s0) - np.asarray(s1)) * rho
    return np.linalg.norm(diff)


def distance_punish(s, a, goal=None, dist_func=l2_norm, unit=1):
    norm = dist_func(s, goal, rho=unit)
    return -100 / (norm)


def distance_mean_reward(s, a, goal=None, dist_func=l2_norm, unit=1):
    norm1 = dist_func(s[:2], goal[0], rho=unit)
    norm2 = dist_func(s[:2], goal[1], rho=unit)
    norm = (norm1 + norm2) / 2
    return 100 / norm


def sigmoid_distance_punish(s, a, goal=None, dist_func=l2_norm, unit=1):
    norm = dist_func(s, goal, rho=unit)
    sigmod = (1.0 + np.exp(-norm))
    return -sigmod / 0.01


def sum_rewards(s=(), a=(), func_lst=[], is_terminal=None):
    reward = sum([f(s, a) for f in func_lst])
    return reward


def test_barrier_function():
    x = np.arange(-10, 10, 0.1)
    y = signod_barrier(x, m=100, s=5)
    plt.plot(x, y, 'k')
    plt.pause(0)


def test_barrier_reward():
    upper = np.array([10, 10])
    lower = np.array([0, 0])
    X = np.arange(-1, 11, 0.1)
    Y = np.arange(-1, 11, 0.1)

    XX, YY = np.meshgrid(X, Y)
    S = np.vstack([XX.flatten(), YY.flatten()]).T
    barrier_func = ft.partial(signod_barrier, c=0, m=100, s=10)
    R = barrier_punish(S, 0, barrier_func=barrier_func,
                       upper=upper, lower=lower)
    Z = R.reshape(XX.shape)
    plt.imshow(Z)
    plt.pause(0)


# test = distance_punish_sigmod(s=(3,4),a = (1,0), goal=(6,6),dist_func=l2_norm, unit=1)
# print test

# test_barrier_function()
# test_barrier_reward()

def test_sigmoid_distance_punish():
    goal = np.array([6, 6])
    X = np.arange(0, 11, 1)
    Y = np.arange(0, 11, 1)

    XX, YY = np.meshgrid(X, Y)
    S = np.vstack([XX.flatten(), YY.flatten()]).T

    R = sigmoid_distance(S, goal=goal, dist_func=l2_norm, unit=1)

    Z = R.reshape(XX.shape)
    plt.imshow(Z)
    plt.pause(0)


class GetLikelihoodRewardFunction:
    def __init__(self, transitionTable, goalPolicies, intentionScale):
        self.transitionTable = transitionTable
        self.goalPolicies = goalPolicies
        self.intentionScale = intentionScale

    def __call__(self, trueGoal, originalReward):
        likelihoodReward = self.createLikelihoodReward(trueGoal)
        newReward = self.mergeRewards(originalReward, likelihoodReward)
        return(newReward)

    def createLikelihoodReward(self, trueGoal):
        rewardDict = {state: {action: {nextState: self.getLikelihoodRatio(state, nextState, trueGoal) for nextState in self.transitionTable[state][action].keys()}
                              for action in self.transitionTable[state].keys()}
                      for state in self.transitionTable.keys()}
        return(rewardDict)

    def mergeRewards(self, reward1, reward2):
        mergedReward = {state: {action: {nextState: reward1[state][action][nextState] + reward2[state][action][nextState] for nextState in reward2[state][action].keys()}
                                for action in reward2[state].keys()}
                        for state in reward2.keys()}
        return(mergedReward)

    def getLikelihoodRatio(self, state, nextState, goalTrue):
        goalLikelihood = self.getNextStateProbability(state, nextState, goalTrue)
        notGoalLikelihood = sum([self.getNextStateProbability(state, nextState, g)
                                 for g in self.goalPolicies.keys()])
        if notGoalLikelihood == 0:
            notGoalLikelihood = 0.0001
        likelihoodRatio = self.intentionScale * goalLikelihood / notGoalLikelihood
        return(likelihoodRatio)

    def getNextStateProbability(self, state, nextState, goal):
        possibleActionsToNextState = [action for action in self.transitionTable[state]
                                      if nextState in self.transitionTable[state][action]]
        probNextState = sum([self.transitionTable[state][action][nextState] * self.goalPolicies[goal][state][action]
                             for action in possibleActionsToNextState])
        return(probNextState)
