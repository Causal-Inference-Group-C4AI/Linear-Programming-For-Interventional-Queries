from causal_usp_icti.graph.graph import Graph 
from causal_usp_icti.utils.probabilities_helper import ProbabilitiesHelper
from causal_usp_icti.utils.mechanisms_generator import MechanismGenerator
import pandas as pd

def createDictIndex(parents: list[int],rlt:list[int], indexerList: list[int]):
    index: str = ""
    for parNode in parents:
        if parents.index(parNode) == len(parents) - 1:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)])
        else:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)]) + ","
    return index

def generateConstraints(data: pd.DataFrame,dag: Graph, unob: int,consideredCcomp: list[int] ,mechanism:list[dict[str, int]]):
    dag.find_cComponents()
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
        Wc.remove(node)
        for cond in Wc:
            if not(cond in condVars):
                condVars.append(cond)
            if not(cond in usedVars):
                usedVars.append(cond)
        productTerms.append({node:condVars.copy()})
        condVars.clear()
    spaces: list[list[int]] = [range(dag.cardinalities[var]) for var in usedVars] 
    cartesianProduct = MechanismGenerator.generateCrossProducts(listSpaces = spaces)
    for rlt in cartesianProduct:
        prob = 1.
        for term in productTerms:
            for key in term:
                dictTarget[key] = rlt[usedVars.index(key)]
                for cVar in term[key]:
                    dictCond[cVar] = rlt[usedVars.index(cVar)]
            prob *= ProbabilitiesHelper.findConditionalProbability(dataFrame= data, indexToLabel=dag.indexToLabel, targetRealization= dictTarget, conditionRealization= dictCond, v=False)
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
                    key  = createDictIndex(parents=endoParents, rlt= rlt, indexerList= usedVars)
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
    graph: Graph = Graph.parse()
    _,_,mechanism = MechanismGenerator.mechanisms_generator(latentNode =graph.labelToIndex["U1"], endogenousNodes = [graph.labelToIndex["Y"], graph.labelToIndex["X"]], cardinalities=graph.cardinalities , 
                                                        graphNodes = graph.graphNodes, v= False )
    
    df: pd.DataFrame = pd.read_csv("/home/joaog/Cpart/Canonical-Partition/causal_usp_icti/linear_algorithm/balke_pearl.csv")
    probs, decisionMatrix = generateConstraints(data=df ,dag= graph, unob=graph.labelToIndex["U1"],consideredCcomp=[graph.labelToIndex["X"], graph.labelToIndex["Y"]],mechanism=mechanism)
    print(probs)
    print("-------------------")
    print(decisionMatrix)