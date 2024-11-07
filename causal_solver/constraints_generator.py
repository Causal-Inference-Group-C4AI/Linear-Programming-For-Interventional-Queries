## TODO:
# 1 - para cada elemento de allPossibleMechanisms gerar um dicionario que leva a realizacao do domino
# (todos os elementos menos o ultimo) na imagem (ultimo elemento).
# 0 - Para isso precisa de um "header" que explicita qual a realizacao do domino e qual eh a variavel da 
# imagem em cada elemento. Fazer no preproecessamento esse header comum.

from partition_methods.relaxed_problem.python.graph import Graph
import itertools
import pandas as pd

def iflog(verbose: bool, message: str):
    if (verbose):
        print(message)

class solver_middleware:
    def __init__(self, graph: Graph):
        self.graph = graph    
        
    def mechanisms_generator(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], parentsDict: dict[int, list[int]], verbose=True):        
        """
        Gera uma lista com todos os mecanismos para uma c-component - que tenha exatamente uma variavel latente.
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
            if (verbose):
                print(f"For varible {var}:")                        
                print(f"Function domain: {functionDomain}")
                print(f"VarResult: {varResult}")

            for domainCase in functionDomain:
                key: str = ""
                for index, el in enumerate(domainCase):
                    key = key + f"{orderedParents[index]}={el},"
                dictKeys.append(key[:-1])
            
            allCasesList  = allCasesList + varResult
        
        if verbose:
            print(headerArray)
            print(f"Lista com todos os mecanismos possíveis, agrupando os excludentes em um mesmo vetor:\n{allCasesList}")
            print(f"Dict Key: lista com as chaves que podem ser convenientes se montarmos um dicionario: {dictKeys}")        

        allPossibleMechanisms = list(itertools.product(*allCasesList))
        mechanismDicts: list[dict[str, int]] = []
        for index, mechanism in enumerate(allPossibleMechanisms):
            if verbose:
                print(f"{index}) {mechanism}")
            currDict: dict[str, int] = {} 
            for domainIndex, nodeFunction in enumerate(mechanism):
                if verbose:
                    print(f"The node function = {nodeFunction}")
                currDict[dictKeys[domainIndex]] = nodeFunction[-1]
            
            mechanismDicts.append(currDict)

        if (verbose):
            print("Check if the dict is working properly:")
            for mechanismDict in mechanismDicts:
                for key in mechanismDict:
                    print(f"key: {key} & val: {mechanismDict[key]}")
                print("------------")
        
        return allPossibleMechanisms, dictKeys, mechanismDicts

    # P(E|C) = P(E,C) / P(C)    
    def fetchCsv(filepath="/home/c4ai-wsl/projects/Canonical-Partition/causal_solver/balke_pearl.csv"):        
        return pd.read_csv(filepath)    

    def probabilityCalculator(dataFrame, indexToLabel, endoValues: dict[int, int], tailValues: dict[int, int], verbose=True): 
        """
        dataFrame: parsed CSV
        indexToLabel: convert endogenous variables index to label, so that it matches the df header
        endoValues: specify the values assumed by the endogenous variables V
        tailValues: specify the values assumed by the graph tail T
        
        Calculates P(V|T) = P(V,T) / P(T) = #Cases(V,T) / # Cases(T)
        """            

        # Build the tail condition
        conditions = pd.Series(dtype=bool)
        for tailVar in tailValues:
            conditions = conditions & (dataFrame[indexToLabel[tailVar]] == tailValues[tailVar])
        
        tailCount = dataFrame[conditions].shape[0]
        print(f"Count tail case: {tailCount}")    

        if tailCount == 0:
            return 0

        # Add endogenous c-component vars conditions
        for endoVar in endoValues:
            conditions = conditions & (dataFrame[indexToLabel[endoVar]] == endoValues[endoVar])

        fullCount = dataFrame[conditions].shape[0]
        print(f"Count complete case: {fullCount}")    

        return fullCount / tailCount
    
    def checkValues(mechanismDict: dict[str, int], parents: dict[int, list[int]], topoOrder: list[int],
                 conditionalVars: dict[int, int], expectedValues: dict[int, int], v=True):
        """
        For some mechanism in the discretization of a latent variable, as well as a tuple of values for the tail, check
        if the deterministic functions imply the expected values for the variables that belong to the c-component.

        mechanismDict: find the value of a node given its parents - specifies U.
        parents: dict that lists the parents of a variable (in the correct order - the same as in the dict)
        topoOrder: order in which we can run through the c-component without any dependency problems.
        conditionalVars: values taken by the variables in the c-component tail.
        expectedValues: values that should be assumed by the endogenous nodes in the c-component.
        """

        iflog(v, "Debug conditionalVars in dfs")        
        if v:
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
                            cardinalitiesEndo: dict[int,int], endoParents: dict[int, list[int]], topoOrder: list[int], endoIndexToLabel: dict[int, str]):
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
        variablesOrder = tail + endoVars # Will use?
        df = solver_middleware.fetchCsv()
        
        for tailVariable in tail:
            variableSpaces.append(range(cardinalitiesTail[tailVariable]))
        
        for endogenous in endoVars:
            variableSpaces.append(range(cardinalitiesEndo[endogenous]))                

        print(f"State spaces array:\n{variableSpaces}")

        combinationOfSpacesAux = list(itertools.product(*variableSpaces))
        combinationOfSpaces = [list(tupla) for tupla in combinationOfSpacesAux]

        for i, case in enumerate(combinationOfSpaces):
            print(f"{i}) {case}")

        matrix: list[list[int]] = [] # 0s and 1s matrix
        for combination in combinationOfSpaces:            
            print(f"Combination (case): {combination}")
            
            # Generate endoValues and tailValues based on combination + endoVars + tail

            # Tail values:
            tailValues: dict[int, int] = {}
            for index in range(len(tail)):
                tailValues[tail[index]] = combination[index]
            
            # endoValues:
            endoValues: dict[int, int] = {}
            for index in range(len(tail)):
                endoValues[endoVars[index]] = combination[index + len(tail)]
                        
            probability: float = solver_middleware.probabilityCalculator(df, {0: "U", 1: "X", 2: "Y", 3: "Z"},
                                                                         endoValues, tailValues, False) # TODO
            print(f"Probability for this case is {probability}")

            # combination order = tail and then the expected values.            
            systemCoefficients: list[int] = []
            conditionalVars: dict[int, int] = {}
            expectedValues:  dict[int, int] = {}

            print(f"Number of tail vars: {len(tail)}")
            for index in range(len(tail)):
                print(f"var = {tail[index]} has value {combination[index]} in the combination")
                conditionalVars[tail[index]] = combination[index]

            print(f"Number of expected vars = {len(endoVars)}")
            for index in range(len(tail), len(combination)):
                print(f"index = {index} and endoVar = {endoVars[index - len(tail)]} with value {combination[index]}")
                expectedValues[endoVars[index - len(tail)]] = combination[index]


            print("ConditionalVars dbg:")
            for key in conditionalVars:
                print(f"key: {key} & value: {conditionalVars[key]}")                            

            print("Expected values dbg:")
            for key in expectedValues:
                print(f"key: {key} & value: {expectedValues[key]}")                            
            
            for mechanismDict in mechanismDicts:
                isValid: bool = solver_middleware.checkValues(mechanismDict=mechanismDict, parents=endoParents, topoOrder=topoOrder,
                                                             conditionalVars=conditionalVars, expectedValues=expectedValues, v=False) # TODO - args = combination, latentEl
                systemCoefficients.append(isValid)
            matrix.append(systemCoefficients)
        
        for eq in matrix:
            print(f"Equation: {eq}")
            # TODO: generate the empirical probability for this combination

def testMechanismGenerator():    
    print(f"Test case 1:")
    solver_middleware.mechanisms_generator(0, [3, 6], {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {3: [0, 1, 2], 6: [0, 4, 5] })
    print(f"Test case 2: Balke & Pearl")
    solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testCsvSolverParser():
    solver_middleware.csvParser(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testEquationsGenerator():
    print("Teste for Balke & Pearl")
    #mechanismDicts: dict[str, int], tail: list[int], cardinalitiesTail: dict[int,int], endoVars: list[int],
                            # cardinalitiesEndo: dict[int,int]):        
    _, _, mechanismDicts = solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] }, False)
    print("Checking the dictionary")
    for element in mechanismDicts:
        for key in element:
            print(f"Key = {key} & value = {element[key]}")
        print ("--------")
        
    # Balke & Pearl graph in which: Z = 3, U = 0, X = 1, Y = 2
    print("\n=== Call equation generator ===\n")
    solver_middleware.equations_generator(mechanismDicts, [3], {3: 2}, [1, 2], {1: 2, 2: 2}, {1: [3], 2: [1]} ,
                                          [1, 2], {1: "X", 2: "Y", 3: "Z"})    

if __name__ == "__main__":
    #testCsvSolverParser()
    testEquationsGenerator()
