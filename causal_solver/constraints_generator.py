from partition_methods.relaxed_problem.python.graph import Graph
import itertools
import pandas as pd

class solver_middleware:            
    def mechanisms_generator(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], parentsDict: dict[int, list[int]], v=True):
        """
        Generates an enumeration (list) of all mechanism a latent value can assume in its c-component. The c-component has to have
        exactly one latent variable.        
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
            # print(functionDomain)

            # Valores possíveis para c
            imageValues: list[int] = range(cardinalities[var])            
            
            varResult = [[domainCase + [c] for c in imageValues] for domainCase in functionDomain]
            if v:
                print(f"For varible {var}:")                        
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
            print(f"Lista com todos os mecanismos possíveis, agrupando os excludentes em um mesmo vetor:\n{allCasesList}")
            print(f"Dict Key: lista com as chaves que podem ser convenientes se montarmos um dicionario: {dictKeys}")        

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
            print("Check if the dict is working properly:")
            for mechanismDict in mechanismDicts:
                for key in mechanismDict:
                    print(f"key: {key} & val: {mechanismDict[key]}")
                print("------------")
        
        return allPossibleMechanisms, dictKeys, mechanismDicts
    
    def fetchCsv(filepath="balke_pearl.csv"):        
        prefix = "/home/c4ai-wsl/projects/Canonical-Partition/causal_solver/"
        return pd.read_csv(prefix + filepath)    

    def probabilityCalculator(dataFrame, indexToLabel, endoValues: dict[int, int], tailValues: dict[int, int], v=True): 
        """
        dataFrame   : parsed CSV
        indexToLabel: convert endogenous variables index to label, so that it matches the df header
        endoValues  : specify the values assumed by the endogenous variables V
        tailValues  : specify the values assumed by the graph tail T
        
        Calculates: P(V|T) = P(V,T) / P(T) = #Cases(V,T) / # Cases(T)
        """            

        # Build the tail condition
        conditions = pd.Series([True] * len(dataFrame), index=dataFrame.index)
        for tailVar in tailValues:
            if v:
                print(f"Index to label of tail variable: {indexToLabel[tailVar]}")
                print(f"Should be equal to: {tailValues[tailVar]}")
            conditions &= (dataFrame[indexToLabel[tailVar]] == tailValues[tailVar])
            
        tailCount = dataFrame[conditions].shape[0]
        if v:
            print(f"Count tail case: {tailCount}")    

        if tailCount == 0:
            return 0

        # Add endogenous c-component vars conditions        
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
    
    def checkValues(mechanismDict: dict[str, int], parents: dict[int, list[int]], topoOrder: list[int],
                 conditionalVars: dict[int, int], expectedValues: dict[int, int], v=True):
        """
        For some mechanism in the discretization of a latent variable, as well as a tuple of values for the tail, check
        if the set of deterministic functions implies the expected values for the variables that belong to the c-component.

        mechanismDict  : find the value of a node given its parents - specifies U.
        parents        : dict that lists the parents of a variable (in the correct order - the same as in the dict)
        topoOrder      : order in which we can run through the c-component without any dependency problems.
        conditionalVars: values taken by the variables in the c-component tail.
        expectedValues : values that should be assumed by the endogenous nodes in the c-component.
        """

        if v:
            print("Debug conditionalVars in dfs")        
            for key in conditionalVars:
                print(f"key: {key} - value: {conditionalVars[key]}")

        isValid: bool = True
        for node in topoOrder:
            dictKey: str = ""
            if v:
                print(f"Check node: {node}")
            for parentOfNode in parents[node]:                
                if v:
                    print(f"Parent node: {parentOfNode}")
                    print(f"Assumes value {conditionalVars[parentOfNode]}")
                dictKey += f"{parentOfNode}={conditionalVars[parentOfNode]},"
            
            if v:
                print(f"key: {dictKey}")
            nodeValue = mechanismDict[dictKey[:-1]] # exclude an extra comma
            conditionalVars[node] = nodeValue
            if nodeValue != expectedValues[node]:
                isValid = False
                break
        
        if isValid:
            return 1
        else:
            return 0
    
    def equations_generator(mechanismDicts: dict[str, int], tail: list[int], cardinalitiesTail: dict[int,int], endoVars: list[int],
                            cardinalitiesEndo: dict[int,int], endoParents: dict[int, list[int]], topoOrder: list[int], endoIndexToLabel: dict[int, str], filepath: str, 
                            precision: int, v: True):
        """
        Generate the system of equations that represents the constraints over a c-component, supposing that only the latent 
        variable states are used as variables in the optimization problem.
        1) Create an array with the spaces of each variable (belonging to the c-component or to the tail)
        2) Cross product on it to generate an enumeration of all cases
        3) Each element that results from the cross product represents one equation in the optimization system. In order
        to fill the line with the coefficients, which will all be 0 or 1, we need to check if each mechanism implies the 
        expected output given the tail.
        4) For the LHS of the linear system we need the empirical probabilities, which will come from the operations
        on the data frame. Use that P(X|Y) = P(X,Y) / P(Y) = #El(X=x,Y=y) / #El(Y=y)
        """
        
        variableSpaces: list[list[int]] = []
        # variablesOrder = tail + endoVars
        df = solver_middleware.fetchCsv(filepath)
        
        for tailVariable in tail:
            variableSpaces.append(range(cardinalitiesTail[tailVariable]))
        
        for endogenous in endoVars:
            variableSpaces.append(range(cardinalitiesEndo[endogenous]))                

        if v:
            print(f"State spaces array:\n{variableSpaces}")

        combinationOfSpacesAux = list(itertools.product(*variableSpaces))
        combinationOfSpaces = [list(tupla) for tupla in combinationOfSpacesAux]

        if v:
            for i, case in enumerate(combinationOfSpaces):
                print(f"{i}) {case}")

        matrix: list[list[int]] = [] # 0s and 1s matrix        
        probabilities: list[float] = []
        
        for combination in combinationOfSpaces:            
            print(f"Combination (case): {combination}")
            
            # Generate endoValues and tailValues based on combination + endoVars + tail

            # Tail values:
            tailValues: dict[int, int] = {}
            for index in range(len(tail)):
                tailValues[tail[index]] = combination[index]
            
            # endoValues:
            endoValues: dict[int, int] = {}
            for index in range(len(endoVars)):
                endoValues[endoVars[index]] = combination[index + len(tail)]
                        
            probability: float = solver_middleware.probabilityCalculator(df, endoIndexToLabel,
                                                                         endoValues, tailValues, False)            
            probability = round(probability * pow(10, precision)) / pow(10, precision)

            probabilities.append(probability)
            # combination order = tail and then the expected values.            
            systemCoefficients: list[int] = []
            conditionalVars: dict[int, int] = {}
            expectedValues:  dict[int, int] = {}
            
            for index in range(len(tail)):
                if v:
                    print(f"var = {tail[index]} has value {combination[index]} in the combination")
                conditionalVars[tail[index]] = combination[index]
            
            for index in range(len(tail), len(combination)):
                if v:
                    print(f"index = {index} and endoVar = {endoVars[index - len(tail)]} with value {combination[index]}")
                expectedValues[endoVars[index - len(tail)]] = combination[index]


            if v:
                print("ConditionalVars dbg:")
                for key in conditionalVars:
                    print(f"key: {key} & value: {conditionalVars[key]}")                            

                print("Expected values dbg:")
                for key in expectedValues:
                    print(f"key: {key} & value: {expectedValues[key]}")                            
            
            for mechanismDict in mechanismDicts:
                isValid: bool = solver_middleware.checkValues(mechanismDict=mechanismDict, parents=endoParents, topoOrder=topoOrder,
                                                             conditionalVars=conditionalVars, expectedValues=expectedValues, v=False) 
                systemCoefficients.append(isValid)
            matrix.append(systemCoefficients)
        
        # Union of U states must have probability one
        probabilities.append(1.0)
        matrix.append([1] * len(mechanismDicts))

        if v:
            for index, eq in enumerate(matrix):
                print(f"{probabilities[index]} - Equation: {eq}")        

        return probabilities, matrix


def testMechanismGenerator():    
    print(f"Test case 1:")
    solver_middleware.mechanisms_generator(0, [3, 6], {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {3: [0, 1, 2], 6: [0, 4, 5] })
    print(f"Test case 2: Balke & Pearl")
    solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testEquationsGenerator():
    print("Teste for Balke & Pearl")
    #mechanismDicts: dict[str, int], tail: list[int], cardinalitiesTail: dict[int,int], endoVars: list[int],
                            # cardinalitiesEndo: dict[int,int]):        
    _, _, mechanismDicts = solver_middleware.mechanisms_generator(0, [1, 2], {1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] }, False)
    print("Checking the dictionary")
    for element in mechanismDicts:
        for key in element:
            print(f"Key = {key} & value = {element[key]}")
        print ("--------")
        
    # Balke & Pearl graph in which: Z = 3, U = 0, X = 1, Y = 2
    print("\n=== Call equation generator ===\n")
    probabilities, equations = solver_middleware.equations_generator(mechanismDicts, [3], {3: 2}, [1, 2], {1: 2, 2: 2}, {1: [3], 2: [1]} ,
                                          [1, 2], {0: "U", 1: "X", 2: "Y", 3: "Z"}, "balke_pearl.csv", 3, False)    

    for i, eq in enumerate(equations):
        print(f"Equation {i}: {probabilities[i]} = {eq} * U^T")

    # 1) Montar na mao a funcao objetivo do Balke Pearl para ver se ja funcionaria
    # 1.1) Create a function that generates the linear programming problem given the equations, the variables, the inequatilities
    # and the objective function

    # 2) Automatizar a geracao da funcao objetivo (que pode ser nao linear :( )

def testItau():
    print("Teste grafo itau")

    _, _, mechanismDicts = solver_middleware.mechanisms_generator(0, [1, 2], {1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1, 3] }, False)
    print("Checking the dictionary")
    for element in mechanismDicts:
        for key in element:
            print(f"Key = {key} & value = {element[key]}")
        print ("--------")
        
    # Itau graph in which: U = 0, T = 1, Y = 2, D = 3
    print("\n=== Call equation generator ===\n")
    probabilities, equations = solver_middleware.equations_generator(mechanismDicts, [3], {3: 2}, [1, 2], {1: 2, 2: 2}, {1: [3], 2: [1, 3]} ,
                                          [1, 2], {0: "U", 1: "T", 2: "Y", 3: "D"}, "itau.csv", 3, False)    

    for i, eq in enumerate(equations):
        print(f"Equation {i}: {probabilities[i]} = {eq} * U^T")


if __name__ == "__main__":    
    # testEquationsGenerator()
    testItau()
