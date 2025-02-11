import numpy as np
import pandas as pd
from utils.graph import Graph
from test_cases.generator.probabilityGen import distribution
from test_cases.generator.generator import generateMechanisms

def dataGen(graph : Graph, numSamp = int(1e3)):
    distExogen : list[np.array] = distribution(graph)
    truthTable : list[list[np.array]] = generateMechanisms(graph)
     
    experiment : list[list[int]] = []
    for _ in range(numSamp):
        vals : list[int] = np.zeros(graph.numberOfNodes, dtype= int)

        exogen_vals: list[int] = [np.random.choice(a = np.arange(1, len(dist) + 1),  p = dist) for dist in distExogen]
    
        for node in graph.topologicalOrder:
            if node in graph.exogenous:
               
               vals[node - 1] = exogen_vals[(graph.exogenous).index(node)]
              
            if node in graph.endogenous:
                
                parents_vals : np.array = np.array([vals[j - 1] for j in graph.parents[node]], dtype=int)
                
                for event in truthTable[(graph.endogenous).index(node)]:
                    if (parents_vals == event[:-1]).all():
                        vals[node -1] = event[-1]
            
        if 0 in vals :
            print("data generation failed")
            return None
                    
        experiment.append(vals)
    experiment = [[element - 1 for element in row] for row in experiment]
    
    df = pd.DataFrame(experiment)

    df_label = []
    for i in range(1, graph.numberOfNodes+1):   
        df_label.append(graph.indexToLabel[i])

    df.columns = df_label

    #df.to_csv('outputs/dataGenOutput.csv', index=False)

    return df
if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.numberOfNodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    print(dataGen(graph=graph, numSamp= int(1e3)))       