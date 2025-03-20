import networkx as nx


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


def parse_file(file_path: str):
    with open(file_path, "r") as file:

        numberOfNodes = file.readline().strip()
        numberOfEdges = file.readline().strip()

        numberOfNodes = int(numberOfNodes)
        numberOfEdges = int(numberOfEdges)

        labelToIndex: dict[str, int] = {}
        indexToLabel: dict[int, str] = {}
        adj: list[list[int]] = [[] for _ in range(numberOfNodes)]
        cardinalities: dict[int, int] = {}
        parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

        for i in range(numberOfNodes):
            label, cardinality = file.readline().strip().split()

            cardinality = int(cardinality)
            labelToIndex[label] = i
            indexToLabel[i] = label
            cardinalities[i] = cardinality

        for _ in range(numberOfEdges):
            u, v = file.readline().strip().split()
            uIndex = labelToIndex[u]
            vIndex = labelToIndex[v]
            adj[uIndex].append(vIndex)
            parents[vIndex].append(uIndex)

        return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents


def parse_interface(nodesString: str, edgesString: str):
    nodesAndCardinalitiesList: list[str] = nodesString.split(",")
    numberOfNodes = len(nodesAndCardinalitiesList)

    cardinalities: dict[int, int] = {}
    labelToIndex: dict[str, int] = {}
    indexToLabel: dict[int, str] = {}
    adj: list[list[int]] = [[] for _ in range(numberOfNodes)]
    parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

    for i, element in enumerate(nodesAndCardinalitiesList):
        auxPair = element.split("=")
        cardinalities[i] = auxPair[1]
        labelToIndex[auxPair[0]] = i
        indexToLabel[i] = auxPair[0]
        cardinalities[i] = int(auxPair[1])

    for element in edgesString.split(","):
        elAux = element.split("->")
        fatherIndex = labelToIndex[elAux[0]]
        sonIndex = labelToIndex[elAux[1]]
        adj[fatherIndex].append(sonIndex)
        parents[sonIndex].append(fatherIndex)

    return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents
