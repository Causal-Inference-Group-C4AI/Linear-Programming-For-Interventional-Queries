import numpy as np
import pandas as pd
from partition_methods.relaxed_problem.python.graph import Graph
from test_cases.generator.probabilityGen import distribution
from test_cases.generator.generator import generateMechanisms

def dataGen(graph : Graph, numSamp = int(1e3)):
    
    distExogen : list[np.array] = distribution(graph)
    truthTable : list[list[np.array]] = generateMechanisms(graph)

    experiment : list[list[int]] = []
    print(graph.exogenous)
    for _ in range(numSamp):
        vals : list[int] = np.zeros(graph.num_nodes, dtype= int)

        exogen_vals: list[int] = [np.random.choice(a = np.arange(1, len(dist) + 1),  p = dist) for dist in distExogen]
        for i, node_exog in enumerate(graph.exogenous):
            
            vals[node_exog - 1] = exogen_vals[i] 
        for num_endo, node_endo in enumerate(graph.endogenous):

            parents_vals : np.array = np.array([vals[j - 1] for j in graph.parents[node_endo]], dtype=int)
            for event in truthTable[num_endo]:
                if (parents_vals == event[:-1]).all():
                    vals[node_endo - 1] = event[-1]
        experiment.append(vals)
    return experiment

if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    
    print(data(graph))       