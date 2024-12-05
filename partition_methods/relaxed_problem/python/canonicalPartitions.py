import math
from .logger import Logger
from .graph import Graph

def bound_canonical_partitions(dagComponents: list[list[int]], cardinalities: list[int], parents: list[int]):
    partitions: list[int] = []
    for i, component in enumerate(dagComponents):
        canonical_partition = 1
        for node in component.nodes:
            if cardinalities[node] > 1:
                base = cardinalities[node]
                exponent = 1
                for parent in parents[node]:
                    if cardinalities[parent] > 1:
                        exponent *= cardinalities[parent]
                canonical_partition *= math.pow(base, exponent)
        print(f"For the c-component #{i + 1} the equivalent canonical partition = {int(canonical_partition)}")    
        partitions.append(canonical_partition)
    
    return partitions

def generateRelaxed(graph: Graph, latentCardinalities: list[int]):
    relaxedGraph: str = ""
    unob: str = ""    
    unobCardinalities: str = ", ".join(map(lambda x: str(int(x)), latentCardinalities))
    
    for index, component in enumerate(graph.dagComponents):
        currUnobLabel : str = "U" + str(index)
        unob += f", {currUnobLabel}"        
        for node in component.nodes:
            if graph.cardinalities[node] > 1:             
                relaxedGraph += f", {currUnobLabel} -> {graph.indexToLabel[node]}"                                

    # adicionar arestas que saem do node depois, pois se nao tiver pai exogeno nao pertence a nenhum c-component
    for index, label in graph.indexToLabel.items():
        if graph.cardinalities[index] > 1:
            for node in graph.adj[index]:                
                relaxedGraph += f", {label} -> {graph.indexToLabel[node]}"

    return relaxedGraph[2:], unob[2:], unobCardinalities

def completeRelaxed(verbose=False):
    graph = Graph.parse()
    Graph.find_cComponents(graph)
    if verbose:
        Logger.debugGraph(graph)
        Logger.debugCcomponents(graph)

    latentCardinalities: list[int] = bound_canonical_partitions(graph.dagComponents, graph.cardinalities, graph.parents)

    return generateRelaxed(graph, latentCardinalities)

def main():
    adjRelaxed, unobRelaxed, unobCard = completeRelaxed(verbose=True)

    print(f"Relaxed graph edges: {adjRelaxed} \n \nUnobservable variables: {unobRelaxed} \n \nCardinalities: {unobCard}")

if __name__ == "__main__":
    main()
