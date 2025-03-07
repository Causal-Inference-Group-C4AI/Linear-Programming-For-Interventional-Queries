from Helper import Helper
from scipy.optimize import linprog
from partition_methods.relaxed_problem.python.graph import Graph
import pandas as pd
import time as tm
def trimDecimal(precision: int, value: float):
    return round(pow(10, precision) * value) / pow(10, precision)

def optProblem(objFunction: list[float], Aeq: list[list[float]], Beq: list[float], interval, v: bool):
    lowerBoundSol = linprog(c=objFunction, A_ub=None, b_ub=None, A_eq=Aeq, b_eq=Beq, method="highs", bounds=interval)
    upperBoundSol = linprog(c=[-x for x in objFunction], A_ub=None, b_ub=None, A_eq=Aeq, b_eq=Beq, method="highs", bounds=interval)

    if lowerBoundSol.success:
        lowerBound = trimDecimal(3, lowerBoundSol.fun)
        if v:
            print(f"Optimal distribution = {lowerBoundSol.x}")
            print(f"Obj. function = {lowerBound}")
    else:
        print("Solution not found:", lowerBoundSol.message)

    # Find maximum (uses the negated objective function and changes the sign of the result)
    if upperBoundSol.success:
        upperBound = trimDecimal(3, -upperBoundSol.fun)
        if v:
            print(f"Optimal distribution = {upperBoundSol.x}")
            print(f"Obj. function = {upperBound}")
    else:
        print("Solution not found:", upperBoundSol.message)    
    print(f"[{lowerBound}, {upperBound}]")
    return lowerBound, upperBound

def main(dag : Graph):

    _,_,mechanism = Helper.mechanisms_generator(latentNode =dag.labelToIndex["U1"], endogenousNodes = [dag.labelToIndex["Y"], dag.labelToIndex["X"]], cardinalities=dag.cardinalities , 
                                                        graphNodes = dag.graphNodes, v= False )
    y0: int = 1
    a0: int = 1
    aRlt: dict[int, int] = {}
    bRlt : dict[int, int] = {}
    yRlt : dict[int, int] = {}
    abRlt : dict[int, int] = {}
    c: list[float] = []
    a:list[list[float]] = []
    b_eq: list[float] = []
    df: pd.DataFrame = pd.read_csv("/home/joaog/Cpart/Canonical-Partition/causal_solver/itau.csv")
    bounds : list[tuple[float]] = [(0,1) for _ in range(len(mechanism))]

    yRlt[dag.labelToIndex["Y"]] = y0
    aRlt[dag.labelToIndex["X"]] = a0

    for u in range(len(mechanism)):
        coef = 0
        for b in range(2):
            bRlt[dag.labelToIndex["B"]] = b
            if mechanism[u][str(dag.labelToIndex["A"])+"="+str(a0)] == y0:
                coef += Helper.findConditionalProbability(dataFrame=df, indexToLabel= dag.indexToLabel, targetRealization=yRlt, conditionRealization= bRlt)
        c.append(coef)
    a.append([1 for _ in range(len(mechanism))])
    b_eq.append(1)
    for aVal in range(2):
        for bVal in range(2):
            aux: list[float] = []
            abRlt[dag.labelToIndex["A"]] = aVal
            abRlt[dag.labelToIndex["B"]] = bVal
            b_eq.append(Helper.findProbability(dataFrame=df, indexToLabel= dag.indexToLabel, variableRealizations=abRlt))
            for u in range(len(mechanism)):
                if (mechanism[u][str(dag.labelToIndex["A"])+"="+str(aVal)] == bVal) and (mechanism[u][""] == aVal):
                    aux.append(1.)
                else:
                    aux.append(0.)
            a.append(aux)
    optProblem(objFunction=c,Aeq=a, Beq=b_eq, interval=bounds, v=True )

if __name__ == "__main__":
    dag = Graph.parse()#use itau_simplified
    start = tm.time()
    main(dag= dag)
    end = tm.time()
    print(f"Time taken {end - start}")
