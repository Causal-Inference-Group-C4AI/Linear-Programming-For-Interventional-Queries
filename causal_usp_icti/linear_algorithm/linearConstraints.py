from causal_usp_icti.graph.graph import Graph 
from causal_usp_icti.utils.probabilities_helper import ProbabilitiesHelper
import pandas as pd

def createDictIndex(parents: list[int],rlt:list[int], indexerList: list[int]):
    index: str = ""
    for parNode in parents:
        if parents.index(parNode) == len(parents) - 1:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)])
        else:
            index += str(parNode) + "=" + str(rlt[indexerList.index(parNode)]) + ","
    return index

def generateConstraints(data: pd.DataFrame,dag: Graph, unob: int, mechanism:list[dict[str, int]]):
    dag.find_cComponents()
    cCompNum = -1
    for key in dag.cComponentToUnob:
        if dag.cComponentToUnob[key] == unob:
            cCompNum = key
    cComponent = dag.dagComponents[cCompNum].copy()
    cComponent.remove(unob)
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
        if (node in dag.dagComponents[unob]) and (node in cComponent):
            cCompOrder.append(node)
    cCompOrder.reverse()
    usedVars = cCompOrder.copy()
    while bool(cCompOrder) :
        node = cCompOrder.pop(0)
        condVars = cCompOrder.copy()
        for cond in dag.parents[node]:
            if not(cond in condVars) and cond != unob:
                condVars.append(cond)
        for var in condVars:
            if not(var in usedVars):
                usedVars.append(var)
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
            coef  = 1.
            for var in usedVars:
                if var in cComponent:
                    endoParents: list[int] = dag.parents[var].copy()
                    endoParents.remove(unob)
                    key  = createDictIndex(parents=endoParents, rlt= rlt, indexerList= usedVars)
                    endoParents.clear()
                    if mechanism[u][key] == rlt[usedVars.index(var)]:
                        coef *= 1
                    else:
                        coef *= 0
            aux.append(coef)
        decisionMatrix.append(aux)
    condVars.clear()
    return probs, decisionMatrix
if __name__ == "__main__":
    graph: Graph = Graph.parse()
    _,_,mechanism = ProbabilitiesHelper.mechanisms_generator(latentNode =graph.labelToIndex["U1"], endogenousNodes = [graph.labelToIndex["Y"], graph.labelToIndex["X"]], cardinalities=graph.cardinalities , 
                                                        graphNodes = graph.graphNodes, v= False )
    
    df: pd.DataFrame = pd.read_csv("/home/joaog/Cpart/Canonical-Partition/causal_solver/balke_pearl.csv")
    probs, decisionMatrix = generateConstraints(data=df ,dag= graph, unob=graph.labelToIndex["U1"],mecahanism=mechanism)
    print(probs)
    print("-------------------")
    print(decisionMatrix)