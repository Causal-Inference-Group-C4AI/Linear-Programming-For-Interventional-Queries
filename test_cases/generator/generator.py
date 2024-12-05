from partition_methods.relaxed_problem.python import canonicalPartitions
from partition_methods.relaxed_problem.python.graph import Graph
import numpy as np
import random as rd

def test():    
    adjRelaxed, unobRelaxed, unobCard = canonicalPartitions.completeRelaxed()

    print(f"Relaxed graph edges: {adjRelaxed} \n \nUnobservable variables: {unobRelaxed} \n \nCardinalities: {unobCard}")

def generateMechanisms(graph: Graph):
    mechanisms: list[list[np.array]] = []
    for node in range(1, graph.numberOfNodes + 1):
        if len(graph.parents[node]) > 0:
            listDomains = []
            print(f"Mechanism for node: {node}/{graph.indexToLabel[node]}")
            for i, parentNode in enumerate(graph.parents[node]):                                                
                print(f"pai: {parentNode}/{graph.indexToLabel[parentNode]}")
                listDomains.append(np.arange(1, graph.cardinalities[parentNode] + 1))
                print(f"Ultimo termo: {listDomains[-1]}")                                
            
            print(f"Dominios (todos os casos): {listDomains}")
            
            grids = np.meshgrid(*listDomains, indexing='ij')            
            cartesianProduct = np.stack(grids, axis=-1).reshape(-1, len(listDomains))            
            
            values: list[int] = []
            for _ in range(0,len(cartesianProduct)):
                values.append(rd.randint(1, graph.cardinalities[parentNode]))                
            
            answer = [np.append(arr, elem) for arr, elem in zip(cartesianProduct, values)]
            print(f"Produto cartesiano: {answer}")
            mechanisms.append(answer)
    return mechanisms

if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.numberOfNodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    
    gm = generateMechanisms(graph)
    print(f"Mecanismos obtidos: {gm}")
