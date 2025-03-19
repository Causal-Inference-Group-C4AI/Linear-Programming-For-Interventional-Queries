import networkx as nx

from causal_usp_icti.graph.graph import Graph
from causal_usp_icti.graph.node import Node

# TODO: INTEGRAR PRIMEIRO A EXECUÇÃO COM O PARSE_FILE
# EM QUE NÃO PRECISA COLAR O INPUT, MAS LÊ DIRETO DO FILE

def parse_state(state):
    if isinstance(state, str):
        return [state]
    if isinstance(state, list):
        return state
    raise Exception(f"Input format for {state} not recognized: {type(state)}")

def parse_target(state):
    if isinstance(state, str):
        return state
    raise Exception(f"Input format for {state} not recognized: {type(state)}")


def parse_edges(state):
    if isinstance(state, str):
        # TODO: Verify if it is a valid string
        # TODO: Parse the string into nx.Graph
        return ""
    if isinstance(state, nx.Graph):
        # TODO: Verify if it is a valid string
        # TODO: Parse the string into nx.Graph
        return ""
    if isinstance(state, list):
        # TODO: Verify if it is list of tuples
        # TODO: Parse the tuples into nx.Graph
        return ""
    if isinstance(state, tuple):
        # TODO: Parse the tuples into nx.Graph
        return ""
    raise Exception(f"Input format for {state} not recognized: {type(state)}")


def parse_interface(nodesString: str, edgesString: str):
        nodesAndCardinalitiesList: list[str] = nodesString.split(',')
        numberOfNodes = len(nodesAndCardinalitiesList)

        cardinalities: dict[int, int] = {}; labelToIndex: dict[str, int] = {}; indexToLabel: dict[int, str] = {}
        adj    : list[list[int]] = [[] for _ in range(numberOfNodes)]
        parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

        for i, element in enumerate(nodesAndCardinalitiesList):
            auxPair = element.split('=')
            cardinalities[i] = auxPair[1]
            labelToIndex[auxPair[0]] = i
            indexToLabel[i] = auxPair[0]
            cardinalities[i] = int(auxPair[1])

        for element in edgesString.split(','):            
            elAux = element.split('->')            
            fatherIndex = labelToIndex[elAux[0]] 
            sonIndex = labelToIndex[elAux[1]]
            adj[fatherIndex].append(sonIndex)
            parents[sonIndex].append(fatherIndex)

        return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents
