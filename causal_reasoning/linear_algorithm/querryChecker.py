from itertools import product
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame

def checkQuerry(N,M,y0,x0):
    df: pd.DataFrame = getScalableDataFrame(N=N,M=M)
    prob = 0 
    for rlt in list(product([0, 1], repeat= 2)):
        term = 1
        term *= ProbabilitiesHelper.find_conditional_probability2(dataFrame=df,targetRealization={"Y":y0},conditionRealization={f"A{N}": rlt[0]})
        term *= ProbabilitiesHelper.find_conditional_probability2(dataFrame=df,targetRealization={f"A{N}": rlt[0]},conditionRealization= {"U1": rlt[1], "X": x0})
        term *= ProbabilitiesHelper.find_probability2(dataFrame= df, realizationDict={"U1":rlt[1]})
        prob += term
    return prob
def main():
    df = pd.DataFrame(columns=['N','M','TRUE_VALUE'])
    df.to_csv("true_results.csv", index=False)
    N_M = [(1,1),
            (2,1),
            (3,1),
            (4,1),
            (5,1),
            (1,2),
            (2,2),
            (3,2),
            (4,2),
            (1,3),
            (2,3),
            (3,3)]
    
    for n_m in N_M:
        N, M = n_m
        prob = checkQuerry(N,M,1,1)
        new_row = {'N': N,'M': M,'TRUE_VALUE': prob}
        new_row_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_row_df], ignore_index=True)
        df.to_csv("true_results.csv", index=False)
    #print(f"Check for N = {N} and M = {M}: P(Y={y0}|do(X={x0})) = {prob}")


if __name__ == "__main__":
    main()