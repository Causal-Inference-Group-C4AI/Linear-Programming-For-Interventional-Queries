## TODO:
# 1 - para cada elemento de allPossibleMechanisms gerar um dicionario que leva a realizacao do domino
# (todos os elementos menos o ultimo) na imagem (ultimo elemento).
# 0 - Para isso precisa de um "header" que explicita qual a realizacao do domino e qual eh a variavel da 
# imagem em cada elemento. Fazer no preproecessamento esse header comum.

from partition_methods.relaxed_problem.python.graph import Graph
import itertools
import pandas as pd

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

    def csvParser(endoVars: list[int], cardinalitiesEndo: dict[int, int], tail: list[int], cardinalitiesTail: dict[int, int]):        
        """
        Gerar todos as combinações de valores possíves entre as endógenas e o tail para determinar
        P(V=v|T) em que V é o vetor das variáveis endógenas do c-component e T é o tail destas (pai de algum nó do c-component, porém
        a variável em si não está no c-component).
        1) Buscar dados do CSV e armazenar em data Frame
        2) Gerar todas uma enumeração de todas as possíveis combinações 
        2.1) Seria bom que outra função gerasse essa enumeração? Porque também precisaremos para construir a matriz de zeros e uns.
        2.2) Será que consigo montar a função objetivo a no mesmo bloco? Será que não está relacionada, de alguma forma, com a matriz
        de zeros e uns?    
        3) Percorrer uma lista com tais combinações e computar, para cada uma a probabilidade
        """
        
        df = solver_middleware.fetchCsv()

        conditions = (df["X"] == 0) & (df["Y"] == 0)        
        print(f"Teste de contagem: {df[conditions].shape[0]}")    
    

    def checkDfs():
        """
        For some mechanism in the discretization of a latent variable, as well as a tuple of values for the tail, check
        if the deterministic functions imply the expected values for the variables that belong to the c-component.
        """
        pass
    
    def equations_generator(mechanismDicts: dict[str, int], tail: list[int], cardinalitiesTail: dict[int,int], endoVars: list[int],
                            cardinalitiesEndo: dict[int,int]):
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
        variablesOrder = endoVars + tail
        for endogenous in endoVars:
            variableSpaces.append(range(cardinalitiesEndo[endogenous]))
        
        for tailVariable in tail:
            variableSpaces.append(range(cardinalitiesTail[tailVariable]))

        print(f"State spaces array:\n{variableSpaces}")

        combinationOfSpacesAux = list(itertools.product(*variableSpaces))
        combinationOfSpaces = [list(tupla) for tupla in combinationOfSpacesAux]

        for i, case in enumerate(combinationOfSpaces):
            print(f"{i}) {case}")

        for combination in combinationOfSpaces:
            systemCoefficients: list[int] = []
            for latentEl in mechanismDicts:
                isValid: bool = solver_middleware.checkDfs() # TODO - args = combination, latentEl
                systemCoefficients.append(isValid)

            # generate the empirical probability for this combination

def testMechanismGenerator():    
    print(f"Test case 1:")
    solver_middleware.mechanisms_generator(0, [3, 6], {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {3: [0, 1, 2], 6: [0, 4, 5] })
    print(f"Test case 2: Balke & Pearl")
    solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testCsvSolverParser():
    solver_middleware.csvParser(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] })

def testEquationsGenrator():
    print("Teste for Balke & Pearl")
    #mechanismDicts: dict[str, int], tail: list[int], cardinalitiesTail: dict[int,int], endoVars: list[int],
                            # cardinalitiesEndo: dict[int,int]):        
    allPossibleMechanisms, dictKeys, mechanismDicts = solver_middleware.mechanisms_generator(0, [1, 2], {0: 2, 1: 2, 2: 2, 3: 2}, {1: [0, 3], 2: [0, 1] }, False)
    print("Checking the dictionary")
    for element in mechanismDicts:
        for key in element:
            print(f"Key = {key} & value = {element[key]}")
        print ("--------")
        
    solver_middleware.equations_generator(mechanismDicts, [3], {3: 2}, [1, 2], {1: 2, 2: 2})

if __name__ == "__main__":
    testCsvSolverParser()
    testEquationsGenrator()
