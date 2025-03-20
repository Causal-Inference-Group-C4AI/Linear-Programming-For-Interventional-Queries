import os
import argparse

import pandas as pd

from causal_usp_icti.graph.graph import Graph, get_graph
from causal_usp_icti.utils.mechanisms_generator import MechanismGenerator
from causal_usp_icti.utils.probabilities_helper import ProbabilitiesHelper
from causal_usp_icti.utils._enum import DirectoriesPath


def create_dict_index(parents: list[int],rlt:list[int], indexerList: list[int]):
    index: str = ""
    for parNode in parents:
        if parents.index(parNode) == len(parents) - 1:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)])
        else:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)]) + ","
    return index

def generate_constraints(data: pd.DataFrame,dag: Graph, unob: int,consideredCcomp: list[int] ,mechanism:list[dict[str, int]]):
    topoOrder: list[int] = dag.topologicalOrder
    cCompOrder: list[int] = []
    probs: list[float] = [1.]
    condVars: list[int] = []
    usedVars : list[int] = []
    productTerms : list[dict[int, list[int]]] = []
    dictTarget: dict[int, int] = {}
    dictCond : dict[int,int] = {}
    decisionMatrix : list[list[int]] = [[1 for _ in range(len(mechanism))]]
    for node in topoOrder:
        if (unob in dag.graphNodes[node].parents) and (node in consideredCcomp):
            cCompOrder.append(node)
    cCompOrder.reverse()
    usedVars = cCompOrder.copy()
    Wc: list[int] = cCompOrder.copy()
    for cCompNode in cCompOrder:
        for par in dag.parents[cCompNode]:
            if not(par in Wc) and (par != unob):
                Wc.append(par)

    while bool(cCompOrder):
        node = cCompOrder.pop(0)
        for cond in Wc:
            if topoOrder.index(cond) < topoOrder.index(node):
                if not(cond in condVars):
                    condVars.append(cond)
                if not(cond in usedVars):
                    usedVars.append(cond)
        productTerms.append({node:condVars.copy()})
        condVars.clear()
    spaces: list[list[int]] = [range(dag.cardinalities[var]) for var in usedVars] 
    cartesianProduct = MechanismGenerator.generate_cross_products(listSpaces = spaces)
    for rlt in cartesianProduct:
        prob = 1.
        for term in productTerms:
            for key in term:
                dictTarget[key] = rlt[usedVars.index(key)]
                for cVar in term[key]:
                    dictCond[cVar] = rlt[usedVars.index(cVar)]
            prob *= ProbabilitiesHelper.find_conditional_probability(dataFrame= data, indexToLabel=dag.indexToLabel, targetRealization= dictTarget, conditionRealization= dictCond, v=False)
            dictTarget.clear()
            dictCond.clear()
        probs.append(prob)
        aux: list[int] = []
        for u in range(len(mechanism)):
            coef: bool  = True
            for var in usedVars:
                if var in consideredCcomp:
                    endoParents: list[int] = dag.parents[var].copy()
                    endoParents.remove(unob)
                    key  = create_dict_index(parents=endoParents, rlt= rlt, indexerList= usedVars)
                    endoParents.clear()
                    if mechanism[u][key] == rlt[usedVars.index(var)]:
                        coef *= 1
                    else:
                        coef *= 0
                        break
            aux.append(float(coef))
        decisionMatrix.append(aux)
    condVars.clear()
    return probs, decisionMatrix
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets causal inference under Partial-Observability."
    )
    parser.add_argument('input_filename',
                        help='The name of the input file in test_case/input directory'
                        )
    parser.add_argument('csv_filename',
                        help='The name of the csv'
                        )
    args = parser.parse_args()
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../../{DirectoriesPath.TEST_CASES_INPUTS.value}/{args.input_filename}.txt")
    graph = get_graph(file_path)
    _,_,mechanism = MechanismGenerator.mechanisms_generator(latentNode =graph.labelToIndex["U1"], endogenousNodes = [graph.labelToIndex["Y"], graph.labelToIndex["X"]], cardinalities=graph.cardinalities , 
                                                        graphNodes = graph.graphNodes, v= False )
        
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../../{DirectoriesPath.CSV_PATH.value}/{args.csv_filename}.csv")
    df: pd.DataFrame = pd.read_csv(csv_path)

    probs, decisionMatrix = generate_constraints(data=df ,dag= graph, unob=graph.labelToIndex["U1"],consideredCcomp=[graph.labelToIndex["X"], graph.labelToIndex["Y"]],mechanism=mechanism)
    print(probs)
    print("-------------------")
    print(decisionMatrix)
