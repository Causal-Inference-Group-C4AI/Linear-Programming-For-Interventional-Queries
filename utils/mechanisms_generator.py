import itertools
from causal_solver.Node import Node
from collections import namedtuple

dictAndIndex = namedtuple('dictAndIndex', ['mechanisms', 'index'])

class MechanismGenerator:
    def helperGenerateSpaces(nodes: list[int], cardinalities: dict[int, int]):
            spaces: list[list[int]] = []
        
            for node in nodes:
                spaces.append(range(0,cardinalities[node]))
        
            return spaces

    def generateCrossProducts(sets: list[list[int]]):
        crossProductsTuples = itertools.product(*sets)
        return [list(combination) for combination in crossProductsTuples]


    def mechanisms_generator(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], graphNodes: list[Node], v=True):
        """
        Generates an enumeration (list) of all mechanism a latent value can assume in its c-component. The c-component has to have
        exactly one latent variable.

        latentNode: an identifier for the latent node of the c-component
        endogenousNodes: list of endogenous node of the c-component
        cardinalities: dictionary with the cardinalities of the endogenous nodes. The key for each node is the number that represents
        it in the endogenousNode list
        parentsDict: dictionary that has the same key as the above argument, but instead returns a list with the parents of each endogenous
        node. PS: Note that some parents may not be in the c-component, but the ones in the tail are also necessary for this function, so they
        must be included.
        v (verbose): enable or disable the logs
        """

        auxSpaces: list[list[int]] = []
        headerArray: list[str] = []
        allCasesList: list[list[list[int]]] = []
        dictKeys: list[str] = []

        for var in endogenousNodes:
            auxSpaces.clear()
            header: str = f"determines variable: {var}"
            amount: int = 1
            orderedParents: list[int] = []
            for parent in graphNodes[var].parents:
                if parent != latentNode:
                    orderedParents.append(parent)
                    header = f"{parent}, " + header
                    auxSpaces.append(range(cardinalities[parent]))
                    amount *= cardinalities[parent]

            headerArray.append(header + f" (x {amount})")
            functionDomain: list[list[int]] = [list(auxTuple) for auxTuple in itertools.product(*auxSpaces)]
            if v:
                print(functionDomain)

            imageValues: list[int] = range(cardinalities[var])

            varResult = [[domainCase + [c] for c in imageValues] for domainCase in functionDomain]
            if v:
                print(f"For variable {var}:")          
                print(f"Function domain: {functionDomain}")
                print(f"VarResult: {varResult}")

            for domainCase in functionDomain:
                key: str = ""
                for index, el in enumerate(domainCase):
                    key = key + f"{orderedParents[index]}={el},"
                dictKeys.append(key[:-1])

            allCasesList  = allCasesList + varResult

        if v:
            print(headerArray)
            print(f"List all possible mechanism, placing in the same array those that determine the same function:\n{allCasesList}")
            print(f"List the keys of the dictionary (all combinations of the domains of the functions): {dictKeys}")        

        allPossibleMechanisms = list(itertools.product(*allCasesList))
        mechanismDicts: list[dict[str, int]] = []
        for index, mechanism in enumerate(allPossibleMechanisms):
            if v:
                print(f"{index}) {mechanism}")
            currDict: dict[str, int] = {} 
            for domainIndex, nodeFunction in enumerate(mechanism):
                if v:
                    print(f"The node function = {nodeFunction}")
                currDict[dictKeys[domainIndex]] = nodeFunction[-1]
            
            mechanismDicts.append(currDict)

        if v:
            print("Check if the mechanism dictionary is working as expected:")
            for mechanismDict in mechanismDicts:
                for key in mechanismDict:
                    print(f"key: {key} & val: {mechanismDict[key]}")
                print("------------")

        return allPossibleMechanisms, dictKeys, mechanismDicts

    def mechanismListGenerator(cardinalities: dict[int, int], listU: list[int], setS: set[int], graphNodes: list[Node]):
        mechanismDictsList: list[list[dictAndIndex]] = [] # Same order as in listU
        globalIndex: int = 0
        latentCardinalities: dict[int, int] = {}
        for latentVariable in listU:
            endogenousInS: list[int] = list(set(graphNodes[latentVariable].children) & setS)
            _, _, mechanismDicts = MechanismGenerator.mechanisms_generator(latentNode=latentVariable, endogenousNodes=endogenousInS,
                                            cardinalities=cardinalities,graphNodes=graphNodes,v=False)

            mechanismIndexDict: list[dictAndIndex] = []
            initVal: int = globalIndex
            for mechanismDict in mechanismDicts:
                mechanismIndexDict.append(dictAndIndex(mechanismDict, globalIndex))
                globalIndex += 1

            latentCardinalities[latentVariable] = globalIndex - initVal
            mechanismDictsList.append(mechanismIndexDict)

        return mechanismDictsList, latentCardinalities