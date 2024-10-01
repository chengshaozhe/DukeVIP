import pandas as pd
import os
import glob
DIRNAME = os.path.dirname(__file__)
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind
import researchpy
import seaborn as sns
import sys
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..')))
from scipy.stats import t, norm
from dataAnalysisFunctions import *
pd.set_option('display.width', None)

if __name__ == '__main__':
    resultsPath = os.path.join(os.path.join(DIRNAME, '..'), 'results/Exp1')
    df = pd.concat(map(pd.read_csv, glob.glob(os.path.join(resultsPath, '*.csv'))), sort=False)
    df = df.sort_values(by='name')

    df['stepPerformance'] = df.apply(lambda x: calStepPerformace(eval(x['trajectory'])), axis=1)
    performaceGroup = df.groupby(['name'])['stepPerformance']
    print(researchpy.summarize(performaceGroup))
    print(researchpy.summarize(performaceGroup.mean()))
    sns.barplot(x='name', y='stepPerformance' ,data=df, ci=95, errwidth=1, capsize=.05)


    df['firstIntentionStepHuman'] = df.apply(lambda x: calculateFirstIntentionStep(eval(x['goal'])), axis=1)
    firstIntentionStepGroup = df.groupby(['name'])['firstIntentionStepHuman']
    # print(researchpy.summarize(firstIntentionStepGroup))
    # print(researchpy.summarize(firstIntentionStepGroup.mean()))
    # sns.barplot(x='name', y='firstIntentionStepHuman' ,data=df, ci=95, errwidth=1, capsize=.05)


    plt.show()