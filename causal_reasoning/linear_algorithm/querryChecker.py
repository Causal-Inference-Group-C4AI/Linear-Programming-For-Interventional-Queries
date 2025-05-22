import os
import time as tm
from itertools import product
from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper
import pandas as pd
from causal_reasoning.utils.mechanisms_generator import MechanismGenerator
from causal_reasoning.graph.graph import Graph
from causal_reasoning.utils._enum import Examples
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
def main(N,M,y0,x0):
    prob = checkQuerry(N,M,y0,x0)
    #print(f"Check for N = {N} and M = {M}: P(Y={y0}|do(X={x0})) = {prob}")
if __name__ == "__main__":
    for m in range(1,6):
        for n in range(1,6):
            main(n,m,1,1)