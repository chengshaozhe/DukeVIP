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

def cleanAITraj(AItraj, target1, target2):
    for index, state in enumerate(AItraj):
        if state == target1 or state == target2:
            tureTraj = AItraj[:index+1]
            break
    return tureTraj

if __name__ == '__main__':
    resultsPath = os.path.join(DIRNAME, '..')
    all_files = glob.glob(os.path.join(resultsPath, 'results/Deidentified Movement Pattern Data/*/*/*.csv'))

    li = []

    for filename in all_files:
        df = pd.read_csv(filename)
        if "Joint" in filename:
          df["condition"] = "socialContext_AI"
        elif "1P2G" in filename:
          df["condition"] = "solo"
        elif "Prac" in filename:
          df["condition"] = "prac"
        year = filename.split("/")[10]
        df["age"] = year
        li.append(df)

    allData = pd.concat(li)
    allData = allData.sort_values(by='age')

    prac = allData[allData['condition']=="prac"]
    Exp1 = allData[allData['condition']=="solo"]
    Exp2 = allData[allData['condition']=="socialContext_AI"]

    df = Exp2


    # resultsPath = os.path.join(os.path.join(DIRNAME, '..'), 'results/Exp2')
    # df = pd.concat(map(pd.read_csv, glob.glob(os.path.join(resultsPath, '*.csv'))), sort=False)
    # df = df.sort_values(by='name')

    df['trajectoryPlayer2'] = df.apply(lambda x: cleanAITraj(eval(x['trajectoryPlayer2']),eval(x['target1Grid']),eval(x['target2Grid'])), axis=1)

# task performace
    df['stepPerformanceHuman'] = df.apply(lambda x: calStepPerformace(eval(x['trajectoryPlayer1'])), axis=1)
    df['stepPerformanceDesireAI'] = df.apply(lambda x: calStepPerformace(x['trajectoryPlayer2']), axis=1)
    performaceGroup = df.groupby(['name'])['stepPerformanceHuman']
    print(researchpy.summarize(performaceGroup))
    print(researchpy.summarize(performaceGroup.mean()))
    # sns.barplot(x='name', y='stepPerformanceDesireAI' ,data=df, ci=95, errwidth=1, capsize=.05)


# Avoidance conflict: reached different destination
    df['isReachDiffGoal'] = df.apply(lambda x: isReachDiffGoal(eval(x['goalPlayer1']),eval(x['goalPlayer2'])), axis=1)
    avoidConflitGroup = df.groupby(['name'])["isReachDiffGoal"]
    # print(researchpy.summarize(avoidConflitGroup))
    # print(researchpy.summarize(avoidConflitGroup.mean()))
    # sns.barplot(x='name', y='isReachDiffGoal' ,data=df, ci=95, errwidth=1, capsize=.05)

# Intention revealing
    df['firstIntentionStepHuman'] = df.apply(lambda x: calculateFirstIntentionStep(eval(x['goalPlayer1'])), axis=1)
    df['firstIntentionStepDesireAI'] = df.apply(lambda x: calculateFirstIntentionStep(eval(x['goalPlayer2'])), axis=1)
    firstIntentionStepGroupHuman = df.groupby(['name'])['firstIntentionStepHuman']
    # print(researchpy.summarize(firstIntentionStepGroupHuman))
    # print(researchpy.summarize(firstIntentionStepGroupHuman.mean()))
    # print(researchpy.summarize(df.groupby(['name'])['firstIntentionStepDesireAI'].mean()))
    # sns.barplot(x='name', y='firstIntentionStepDesireAI' ,data=df, ci=95, errwidth=1, capsize=.05)

    # plt.show()

    
    
# isReachDiffGoal ~ firstIntentionStepHuman
    os.environ['R_HOME'] = "/Library/Frameworks/R.framework/Resources"

    from pymer4.models import Lmer

    dfLogit = df
    dfLogit = df[df.age == '5-year-olds']

    model = Lmer("isReachDiffGoal ~ firstIntentionStepDesireAI + (1|name)",
                  data=dfLogit, family = 'binomial')
    print(model.fit())

    ax = sns.regplot(x="firstIntentionStepDesireAI", y="isReachDiffGoal", x_jitter = 0.5,  scatter_kws = {"alpha": 0.1}, data=model.data, fit_reg=True)
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.rcParams['svg.fonttype'] = 'none'

    # plt.xlabel('intetion first revealing step', fontsize=12, color='black')
    plt.ylabel('Reached different destination', fontsize=12, color='black')
    plt.axhline(y=0.5, color='k', linestyle='--', alpha=0.5)
    plt.show()



# isConsiderOther ~ firstIntentionStepHuman
    # statDf = df.groupby(['age','name'])['isReachDiffGoal'].mean().reset_index()
    # statDf['firstIntentionStepHuman'] = df.groupby(['age','name'])['firstIntentionStepHuman'].mean().to_list()

    # statDf['isConsiderOther'] = statDf.apply(lambda x: 1 if abs(x.isReachDiffGoal - 0.5) >= 0.25 else 0, axis=1)
    # print(statDf)

    # ax = sns.barplot(x='isConsiderOther', y='firstIntentionStepHuman',data=statDf, errorbar=('ci', 95), capsize=.05)
    # plt.show()








