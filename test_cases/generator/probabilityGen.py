from partition_methods.relaxed_problem.python.graph import Graph
import numpy as np
import random as rand
def distribution(graph : Graph, prec = 3):
    exogenous, endogenous =  findExogen(graph)
    
    cardinalities : list[int] = np.empty(len(exogenous), dtype= int)
   
    for i, k in enumerate(exogenous):
        cardinalities[i] = graph.cardinalities[k] 
    probs : np.array[np.array[float]] = np.empty(len(cardinalities), dtype = object)
    print(cardinalities)
    for j, card in enumerate(cardinalities):
        dist = np.empty(card)
        for i in range(dist.size):
            dist[i] = rand.uniform(1,100)
        dist = dist/np.sum(dist)
        dist = np.trunc(dist*10**prec)/10**prec
        dist[-1] = 1 - np.sum(dist[0:card-1])        
        probs[j] = dist

    return probs

def findExogen(graph : Graph):
    exogenIndex : list[int]  = []
    endogenIndex : list[int] = []
    for i in range(1, graph.num_nodes + 1):
        if not (bool(graph.parents[i])) :
           exogenIndex.append(i)
        else :
            endogenIndex.append(i)
    return exogenIndex, endogenIndex

if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    print(graph.cardinalities, type(graph.cardinalities[1]))
    
    print(distribution(graph))



        