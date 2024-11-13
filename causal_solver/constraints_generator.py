from partition_methods.relaxed_problem.python.graph import Graph
from scipy.optimize import linprog
import itertools
import pandas as pd

class solver_middleware:            
    def mechanisms_generator(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], parentsDict: dict[int, list[int]], v=True):
        """
        Generates an enumeration (list) of all mechanism a latent value can assume in its c-component. The c-component has to have
        exactly one latent variable.        

        latentNode: an identifier for the latent node of the c-component
        endogenousNodes: list of endogenous node of the c-component
        cardinalities: dictionary with the cardinalities of the endogenous nodes. The key for each node is the number that represents
        it in the endogenousNode list
        parentsDict: dictionary that has the same key as the above argument, but instead returns a list with the parents of each endogenous 
        node. PS: Note that some parents may not be in the c-component, as the tail is also necessary for this function.
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
    
    def fetchCsv(filepath="balke_pearl.csv"):        
        prefix = "/home/c4ai-wsl/projects/Canonical-Partition/causal_solver/"
        return pd.read_csv(prefix + filepath)    

    def probabilityCalculator(dataFrame, indexToLabel, endoValues: dict[int, int], tailValues: dict[int, int], v=True): 
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
    
    def checkValues(mechanismDict: dict[str, int], parents: dict[int, list[int]], topoOrder: list[int],
                 tailValues: dict[int, int], endogenousValues: dict[int, int], v=True):
        """
        For some mechanism in the discretization of a latent variable, as well as a tuple of values for the tail, check
        if the set of deterministic functions implies the expected values for the variables that belong to the c-component.

        mechanismDict    : dictionary that returns the value assumed by a node given (the key) the values of its parents
        parents          : dictionary that return a list of the parents of a variable
        topoOrder        : order in which we can run through the c-component without any dependency problems in the deterministic
                          functions.
        tailValues       : values taken by the variables in the c-component's tail T.
        endogenousValues : values that should be assumed by the endogenous variables V of the c-component
        """

        if v:
            print("Debug tailValues in dfs")        
            for key in tailValues:
                print(f"key: {key} - value: {tailValues[key]}")

        isValid: bool = True
        for node in topoOrder:
            dictKey: str = ""
            if v:
                print(f"Check node: {node}")
            for parentOfNode in parents[node]:                
                if v:
                    print(f"Parent node: {parentOfNode}")
                    print(f"Assumes value {tailValues[parentOfNode]}")
                dictKey += f"{parentOfNode}={tailValues[parentOfNode]},"
            
            if v:
                print(f"key: {dictKey}")
            nodeValue = mechanismDict[dictKey[:-1]] # exclude an extra comma
            tailValues[node] = nodeValue
            if nodeValue != endogenousValues[node]:
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
                                                             tailValues=conditionalVars, endogenousValues=expectedValues, v=False) 
                systemCoefficients.append(isValid)
            matrix.append(systemCoefficients)
        
        # Union of U states must have probability one
        probabilities.append(1.0)
        matrix.append([1] * len(mechanismDicts))

        if v:
            for index, eq in enumerate(matrix):
                print(f"{probabilities[index]} - Equation: {eq}")        

        return probabilities, matrix
    
    # Linear case: same c-component OR tail
    def generateObjectiveFunction(mechanismDicts: list[dict[str,int]], targetVariable: int, targetValue: int, interventionVariable: int, interventionValue: int, topoOrder: list[int],
                                  tail: list[int], tailCardinalities: dict[int,int]):
        """
        generate a linear objective function for the case in which the variable under intervention and the target are in 
        the same c-component (or at least on the tail).

        Algo: for each possible realization of the tail, consider all possile mechanisms. If it implies the expected target value, then it adds
        P(U|T)*P(T) = P(U,T) to the system.

        Important: this can be optimized by marginalizing on irrelevant variables. Hence, the argument tail does NOT need to contain all variables in the tail. In the
        same way, the topoOrder does NOT need to contain all endogenous variables of the c-component
        """

        for mechanism in mechanismDicts:
            for node in topoOrder:
                pass

        pass

    def interventionalQuery(probabilities: list[int], empiricalEquations: list[list[int]], objectiveFunctionPos: list[int],
                             objectiveFunctionNeg: list[int]):
        PosLower, PosUpper = solver_middleware.createLinearProblem(probabilities, empiricalEquations, objectiveFunctionPos)
        NegLower, NegUpper = solver_middleware.createLinearProblem(probabilities, empiricalEquations, objectiveFunctionNeg)

        print(f"The positive query has bounds: [{PosLower},{PosUpper}]")
        print(f"The negative query has bounds: [{NegLower},{NegUpper}]")
        
        finalLower = PosLower - NegUpper
        finalUpper = PosUpper - NegLower
        print(f"The interventional bounds are: [{finalLower},{finalUpper}]")
        pass
    
    def createLinearProblem(probabilities: list[int], empiricalEquations: list[list[int]], objectiveFunction: list[int]):
        """
        Creates a linear programming problem with the following restrictions:
        - Equations from empirical probabilities (from args)
        - The sum of probabilities of a latent variable in its space must add to one (from args)
        - All the variables must be between 0 and 1 (not from args)
        - Objective function (from args)
        """        
        
        # Call the solver
        bounds = [(0, 1) for _ in range(len(objectiveFunction))]
        negObj = [-x for x in objectiveFunction]
        result = linprog(c=objectiveFunction, A_ub=None, b_ub=None, A_eq=empiricalEquations, b_eq=probabilities, method="highs", bounds=bounds)
        resultNeg = linprog(negObj, A_ub=None, b_ub=None, A_eq=empiricalEquations, b_eq=probabilities, method="highs", bounds=bounds)

        # Verify the minimum (lb)
        if result.success:
            # print("Solução ótima encontrada:", result.x)
            print("Valor da função objetivo:", result.fun)
        else:
            print("Solução não encontrada:", result.message)

        # Verify the maximum (ub)
        if result.success:
            # print("Solução ótima encontrada:", resultNeg.x)
            print("Valor da função objetivo:", -resultNeg.fun)
        else:
            print("Solução não encontrada:", resultNeg.message)        
        
        return  result.fun, -resultNeg.fun

def testMechanismGenerator():    
    print(f"Test case 1:")
    solver_middleware.mechanisms_generator(0, [3, 6], {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {3: [0, 1, 2], 6: [0, 4, 5] })
    print(f"Test case 2: Balke & Pearl")
    solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testBalkePearl():
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

    mockObj = [0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, 0]
    mockPos = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    mockNeg = [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]
    solver_middleware.createLinearProblem(probabilities, equations, mockObj)
    
    print("Test the second approach:")
    solver_middleware.interventionalQuery(probabilities, equations, mockPos, mockNeg)

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
    testBalkePearl()
    #testItau()
