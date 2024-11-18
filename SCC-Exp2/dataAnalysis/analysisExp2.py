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

def coordination_type(isReachDiffGoal_value):
    if isReachDiffGoal_value >= 0.75:
        return "preferDifferent"
    elif isReachDiffGoal_value <= 0.25:
        return "preferSame"
    else:
        return "no-coordination"

if __name__ == '__main__':
    resultsPath = os.path.join(DIRNAME, '..')
    all_files = glob.glob(os.path.join(resultsPath, 'results/data/*/*/*.csv'))

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

    Exp1['firstIntentionStep'] = Exp1.apply(lambda x: calculateFirstIntentionStep(eval(x['goal'])), axis=1)

    Exp2['stepPerformance'] = Exp2.apply(lambda x: calStepPerformace(eval(x['trajectoryPlayer1'])), axis=1)

    Exp2['totalTime'] = Exp2.apply(lambda x: sum(eval(x['reactionTime'])), axis=1)
    maxTime = 1*60*1000
    Exp2 = Exp2[Exp2['totalTime'].astype(int) <= maxTime]

    Exp2['trajectoryPlayer2'] = Exp2.apply(lambda x: cleanAITraj(eval(x['trajectoryPlayer2']),eval(x['target1Grid']),eval(x['target2Grid'])), axis=1)

# task performace
    Exp2['stepPerformanceHuman'] = Exp2.apply(lambda x: calStepPerformace(eval(x['trajectoryPlayer1'])), axis=1)
    Exp2['stepPerformanceDesireAI'] = Exp2.apply(lambda x: calStepPerformace(x['trajectoryPlayer2']), axis=1)

# Avoidance conflict: reached different destination
    Exp2['isReachDiffGoal'] = Exp2.apply(lambda x: isReachDiffGoal(eval(x['goalPlayer1']),eval(x['goalPlayer2'])), axis=1)

    statDfExp2 = Exp2.groupby(['age','name'])['isReachDiffGoal'].mean().reset_index()
    statDfExp2['isConsiderOther'] = statDfExp2.apply(lambda x: 1 if abs(x.isReachDiffGoal - 0.5) >= 0.25 else 0, axis=1)
    statDfExp2['coordinationType'] = statDfExp2['isReachDiffGoal'].apply(coordination_type)

    Exp2 = pd.merge(Exp2, statDfExp2[['age', 'name', 'isConsiderOther','coordinationType']], on=['age', 'name'], how='left')


# Plot number of isConsiderOther per name by age
    # plt.figure(figsize=(10, 6))
    # sns.barplot(x='age', y='isConsiderOther', data=statDfExp2, ci=95, errwidth=1, capsize=.05)
    # plt.title('Consideration of Others by Age')
    # plt.xlabel('Age Group')
    # plt.ylabel('Proportion Considering Others')
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()

# Intention revealing
    Exp2['firstIntentionStep'] = Exp2.apply(lambda x: calculateFirstIntentionStep(eval(x['goalPlayer1'])), axis=1)
    Exp2['firstIntentionStepDesireAI'] = Exp2.apply(lambda x: calculateFirstIntentionStep(eval(x['goalPlayer2'])), axis=1)
    Exp2['firstIntentionStepRT'] = Exp2.apply(lambda x: sum(eval(x['reactionTime'])[:x.firstIntentionStep])/1000, axis=1)


# compared
    combined_df = pd.merge(Exp1, Exp2, on='name', suffixes=('_Exp1', '_Exp2'), how='outer')
    combined_df = combined_df.sort_values(by='age_Exp2')
    print(combined_df.columns)
    combined_df['decision_time_diff'] = combined_df['firstIntentionStep_Exp2'].astype(float) - combined_df['firstIntentionStep_Exp1'].astype(float)

    # sns.barplot(x='age_Exp2', y='decision_time_diff', hue = 'isConsiderOther', data=combined_df, err_kws={'linewidth': 1}, capsize=.1, errorbar=('ci', 95))
    # plt.show()

    os.environ['R_HOME'] = "/Library/Frameworks/R.framework/Resources"
    from pymer4.models import Lmer

    # Predict decision_time_diff from isConsiderOther using mixed effects model
    model_time = Lmer("firstIntentionStepRT ~ isConsiderOther + age_Exp2 + (1|name)",
                    data=combined_df)
    model_time2 = Lmer("firstIntentionStepRT ~ isConsiderOther + (1|name)",
                    data=combined_df)
    print(model_time.fit())
    # print(model_time2.fit())

    # Visualize relationship
    plt.figure(figsize=(8, 6))
    # sns.boxplot(x="isConsiderOther", y="firstIntentionStepRT", data=combined_df)
    sns.boxplot(x="age_Exp2", y="firstIntentionStepRT", hue = 'isConsiderOther',  data=combined_df)
    plt.show()
    # plt.xlabel('Considers Others (0=No, 1=Yes)')
    # plt.ylabel('Difference in Decision Time (Exp2 - Exp1)')
    # plt.show()
    zz


# isReachDiffGoal ~ firstIntentionStep

    dfLogit = combined_df
    # dfLogit = df[df.age == '5-year-olds']

    model = Lmer("isReachDiffGoal ~ decision_time_diff + age_Exp2 + (1|name)",
                  data=dfLogit, family = 'binomial')
    print(model.fit())

    ax = sns.regplot(x="decision_time_diff", y="isReachDiffGoal", x_jitter = 0.5,  scatter_kws = {"alpha": 0.1}, data=model.data, fit_reg=True)
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.rcParams['svg.fonttype'] = 'none'

    # plt.xlabel('intetion first revealing step', fontsize=12, color='black')
    # plt.ylabel('Reached different destination', fontsize=12, color='black')
    plt.axhline(y=0.5, color='k', linestyle='--', alpha=0.5)
    plt.show()



# isConsiderOther ~ firstIntentionStep
    # statDf = df.groupby(['age','name'])['isReachDiffGoal'].mean().reset_index()
    # statDf['firstIntentionStep'] = df.groupby(['age','name'])['firstIntentionStep'].mean().to_list()

    # statDf['isConsiderOther'] = statDf.apply(lambda x: 1 if abs(x.isReachDiffGoal - 0.5) >= 0.25 else 0, axis=1)
    # print(statDf)

    # ax = sns.barplot(x='isConsiderOther', y='firstIntentionStep',data=statDf, errorbar=('ci', 95), capsize=.05)
    # plt.show()








