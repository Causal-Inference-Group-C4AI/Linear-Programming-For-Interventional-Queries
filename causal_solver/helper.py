import pandas as pd
import itertools

class helper:
    """
    Common methods used to create the optimization problem
    """
    def findConditionalProbability(dataFrame, indexToLabel, endoValues: dict[int, int], tailValues: dict[int, int], v=True):
        """
        dataFrame   : pandas dataFrama that contains the data from the csv
        indexToLabel: dictionary that converts an endogenous variable index to its label
        endoValues  : specifies the values assumed by the endogenous variables V
        tailValues  : specifies the values assumed by the c-component tail T
        
        Calculates: P(V|T) = P(V,T) / P(T) = # Rows(V,T) / # Rows(T)
        """            

        # Build the tail condition
        conditions = pd.Series([True] * len(dataFrame), index=dataFrame.index)        
        for tailVar in tailValues:
            print(f"Test tail var: {tailVar}")
            if v:
                print(f"Index to label of tail variable: {indexToLabel[tailVar]}")
                print(f"Should be equal to: {tailValues[tailVar]}")
            conditions &= (dataFrame[indexToLabel[tailVar]] == tailValues[tailVar])
            
        tailCount = dataFrame[conditions].shape[0]
        if v:
            print(f"Count tail case: {tailCount}")    

        if tailCount == 0:
            return 0

        # Add the endogenous c-component variables conditions        
        for endoVar in endoValues:
            if v:
                print(f"Index to label of endogenous variable: {indexToLabel[endoVar]}")
                print(f"Should be equal to: {endoValues[endoVar]}")
            conditions = conditions & (dataFrame[indexToLabel[endoVar]] == endoValues[endoVar])

        fullCount = dataFrame[conditions].shape[0]
        
        if v:
            print(f"Count of all conditions: {fullCount}")            
            print(f"Calculated probability: {fullCount / tailCount}")        
            print("--------------\n\n")

        return fullCount / tailCount
    
    def findTailProbability(dataFrame, indexToLabel, tailValues: dict[int, int], v=True): 
        # Build the tail condition
        conditions = pd.Series([True] * len(dataFrame), index=dataFrame.index)        
        for tailVar in tailValues:            
            if v:
                print(f"Test tail var: {tailVar}")
                print(f"Index to label of tail variable: {indexToLabel[tailVar]}")
                print(f"Should be equal to: {tailValues[tailVar]}")
            conditions &= (dataFrame[indexToLabel[tailVar]] == tailValues[tailVar])
            
        tailCount = dataFrame[conditions].shape[0]
        if v:
            print(f"Count tail case: {tailCount}")                    
            print(f"Total cases: {dataFrame.shape[0]}")

        return tailCount / dataFrame.shape[0]

    def helperGenerateSpaces(nodes: list[int], cardinalities: dict[int, int]):
        spaces: list[list[int]] = []
        for node in nodes:
            spaces.append(range(0,cardinalities[node]))
        
        return spaces
    
    def fetchCsv(filepath="balke_pearl.csv"):        
        prefix = "/home/c4ai-wsl/projects/Canonical-Partition/causal_solver/"
        return pd.read_csv(prefix + filepath)

    def generateCrossProducts(sets: list[list[int]]):        
        crossProductsTuples = itertools.product(*sets)
        return [list(combination) for combination in crossProductsTuples]
    
    def mechanisms_generator(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], parentsDict: dict[int, list[int]], v=True):
        """
        Generates an enumeration (list) of all mechanism a latent value can assume in its c-component. The c-component has to have
        exactly one latent variable.

        latentNode: an identifier for the latent node of the c-component
        endogenousNodes: list of endogenous node of the c-component
        cardinalities: dictionary with the cardinalities of the endogenous nodes. The key for each node is the number that represents
        it in the endogenousNode list
        parentsDict: dictionary that has the same key as the above argument, but instead returns a list with the parents of each endogenous
        node. PS: Note that some parents may not be in the c-component, but the ones in the tail are also necessary for this function.
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
            for parent in parentsDict[var]:
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
