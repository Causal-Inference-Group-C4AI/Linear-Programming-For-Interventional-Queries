import itertools
from collections import namedtuple
import pandas as pd

latentAndCcomp = namedtuple('latentAndCcomp', ['latent', 'nodes'])
dictAndIndex   = namedtuple('dictAndIndex', ['mechanisms', 'index'])

class case1Solver:
    """
    Determines the a "supertail" T of a set of endogenous variables V associated to a set of latent variables
    U such that T and U fully determine V and T and U are indepedent. We consider that the independency hypothesis
    are already inserted in the graph and assume d-separation to be its equivalent.
    The case1 is when both the variable under intervention as well as the target variable are in the same c-component
    """    

    def objetiveFunctionBuilder(latentIntervention: int, cComponentIntervention: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]],
                                cardinalities: dict[int, int], cCompDict: dict[int, list[int]],
                                interventionVariable: int, interventionValue, targetVariable: int, 
                                targetValue: int, topoOrder: list[int], filepath: str,
                                indexToLabel: dict[int, str], v: bool):
        """
        Tests all cases of the tail and of the mechanisms in order to build the objective function.

        latentIntervention: latent variable which is a parent of both the intervention variable in the target variable
        cComponentIntervention: complete cComponent in which the intervention variable and the target variable are
        outNode: from each node as a key it returns a list with all the nodes that can be accessed from it (arrow points out of the node)
        inNode: from each node as a key it returns a list with all the nodes that are parents from it
        cardinalities: from each node return the number of states
        cCompDict: from each latent as a key get the complete cComponent (all its children)
        interventionVariable: the variable under intervention - do operator.
        interventionValue: the value that the variable under intervention is fixed on
        targetVariable: the variable we want to measure the probability
        targetValue: the value assumed by such a variable considering the intervention
        topoOrder: a topological order in which we can run through the endogenous nodes (from the whole graph)        
        filepath: path to the CSV file with the experiment results.
        indexToLabel: a dictionary that translates a node index to its label (which is the same as in the CSV)
        """                
        dataFrame = case1Solver.fetchCsv(filepath)

        listS, listT, listU = case1Solver.findSuperTail(latentIntervention, cComponentIntervention, outNode, inNode, False)
        # Remove nodes not in S from topoOrder AND the interventionNode:
        if interventionVariable in topoOrder:
            topoOrder.remove(interventionVariable)
        for node in topoOrder:
            if node not in listS:
                topoOrder.remove(node) 

        # print(f"Debug list S: {listS}")
        # print(f"Debug list U: {listU}")
        # print(f"Debug list T: {listT}")
                    
        # Get the mechanisms from all the relevant latent variables        
        mechanismDictsList: list[list[dict[str, int]]] = [] # Same order as in list U
        for latentVariable in listU:        
            endogenousNodes = cCompDict[latentVariable]
            if latentVariable in endogenousNodes:
                endogenousNodes.remove(latentVariable)

            _, _, mechanismDicts = case1Solver.mechanisms_generator(latentNode=latentVariable,endogenousNodes=endogenousNodes,
                                             cardinalities=cardinalities,parentsDict=inNode,v=False)            
            
            # print(f"Debug mechanisms: {mechanismDicts}")
            mechanismIndexDict: list[dictAndIndex] = []
            for index, mechanismDict in enumerate(mechanismDicts):
                mechanismIndexDict.append(dictAndIndex(mechanismDict, index))                
            
            mechanismDictsList.append(mechanismIndexDict)                        
                
        # Generate all the tail states
        tailVarSpaces: list[list[int]] = []
        for tailVar in listT:
            tailVarSpaces.append(range(0,cardinalities[tailVar]))

        # Generate a cross product between all tail states AND all mechanisms (latent variable states)
        tailCombinationsAux = itertools.product(*(tailVarSpaces))
        tailCombinations = [list(combination) for combination in tailCombinationsAux] # the order is the same as in list T.        
        latentCombinationsAux = itertools.product(*(mechanismDictsList))
        latentCombinations = [list(combination) for combination in latentCombinationsAux]

                
        if v:
            print("-- debug: tailCombinations --")
            for i, tailCombination in enumerate(tailCombinations):            
                print(f"{i}) {tailCombination}") 

            print("-- debug: latentCombinations --")
            for i, latentCombination in enumerate(latentCombinations):            
                print(f"latent combination {i}) {latentCombination}") 

        # Run through each element in the cross product array and check if the desired output is achieved. If so,
        # sum the calculated probability.
        objectiveFunction: dict[str, int] = { } # Key = indexer (from array to str concatenated) and value = coefficient ai
        # F = sum(Prod(P(Uk)) * P(T=t) * 1(T=t,U=u => Y=y)) hence ai = P(T=t) iff 1() = 1 and 0 c.c
        for i, latentCombination in enumerate(latentCombinations):
            totalProbability: float = 0.0
            if v:
                print("---- START LATENT COMBINATION: ----")
                print(f"{latentCombination}")
            indexer: str = ""
            for latentMechanism in latentCombination:                
                indexer += f"{latentMechanism.index}"            
                        
            for tailRealization in tailCombinations:
                if v:
                    print(f"Tail realization: {tailRealization}")
                tailValues: dict[int,int] = {}
                for j, tailValue in enumerate(tailRealization):
                    tailValues[listT[j]] = tailValue
                
                isCompatible = case1Solver.checkRealization(mechanismDictsList=latentCombination,
                                             parents=inNode,
                                             topoOrder=topoOrder,
                                             tailValues=tailValues,
                                             interventionVariable=interventionVariable,
                                             interventionValue=interventionValue,                                             
                                             latentVariables=listU,
                                             targetVariable=targetVariable,
                                             targetValue=targetValue
                                             )                
                if isCompatible:                
                    empiricalProbability = case1Solver.findProbability(dataFrame, indexToLabel, tailValues, False)
                    totalProbability += empiricalProbability            

            print(f"Debug: key = {indexer} and value = {totalProbability}")
            objectiveFunction[indexer] = totalProbability             

        return objectiveFunction

    def fetchCsv(filepath="balke_pearl.csv"):        
        prefix = "/home/c4ai-wsl/projects/Canonical-Partition/causal_solver/"
        return pd.read_csv(prefix + filepath)    
        
    def findProbability(dataFrame, indexToLabel, tailValues: dict[int, int], v=True): 
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

    
    def checkRealization(mechanismDictsList: list[dict[str, int]], parents: dict[int, list[int]], topoOrder: list[int],
                tailValues: dict[int, int], interventionVariable: int, interventionValue: int, latentVariables: list[int], 
                targetVariable: int, targetValue: int):
        """
        For some mechanism in the discretization of a latent variable, as well as a tuple of values for the tail, check
        if the set of deterministic functions implies the expected values for the variables that belong to the c-component.

        mechanismDictsList : list with the realization of each latent variable, in the form of mechanisms
        parents            : dictionary that return a list of the parents of a variable (including the exogenous parent)
        topoOrder          : order in which we can run through the graph without any dependency problems in the deterministic
                             functions.
        tailValues         : values taken by the variables in the c-component's tail T.
        endogenousValues   : values that should be assumed by the endogenous variables V of the c-component
        """        
        
        computedNodes: dict[int, int] = {interventionVariable: interventionValue}
        for key in tailValues:
            computedNodes[key] = tailValues[key]
    
        for node in topoOrder:
            dictKey: str = ""                                    
            for parentOfNode in parents[node]:                                                
                if parentOfNode not in latentVariables:
                    dictKey += f"{parentOfNode}={computedNodes[parentOfNode]},"
                else:                    
                    nodeLatentParent: int = parentOfNode
            
            for i, latentVar in enumerate(latentVariables):
                if latentVar == nodeLatentParent:
                    nodeLatentParentIndex: int = i
                    break
            
            nodeValue = mechanismDictsList[nodeLatentParentIndex].mechanisms[dictKey[:-1]] # exclude an extra comma
            
            computedNodes[node] = nodeValue            

        return computedNodes[targetVariable] == targetValue

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

    def findSuperTail(latent: int, cComponent: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]], v: bool):
        """
        Given a graph, the node under intervention and the target node, it computes the supertail T and the set of latent
        variables U such that T and U are independent
        """
        # Initialize the sets
        listU: list[int] = [latent] # Latent variables to be taken in account
        listT: list[int] = [] # 
        listS: list[int] = []
        
        for node in cComponent: # Complete this procedure before the next
            if node not in listU:
                listS.append(node)
        
        for node in cComponent:
            for parentNode in inNode[node]:
                if (parentNode not in listU) and (parentNode not in listS):
                    listT.append(parentNode) # Adds the parents to the tail

        if v:
            print("--- Debug initialization ---")
            print(f"List U: {listU}")
            print(f"List S: {listS}")
            print(f"List T: {listT}")

        
        # Remember to come back to the beginning of the list if some new latent is added!
        tailIndex = 0
        while tailIndex < len(listT):
            tailVar = listT[tailIndex]
            # Check independency with the latent variables!        
            if v:
                print(f"Check indep for tail var: {tailVar}")
                print(f"--- check each latent ---")
            tailIndepU = True
            for latentVar in listU:                                
                independency = case1Solver.dSeparationChecker(tailVar, latentVar, outNode, inNode)
                if not independency:                
                    tailIndepU = False
                    break
            
            if not tailIndepU:                
                listT.remove(tailVar)                
                listS.append(tailVar)
                
                resetFlag: bool = False                                
                for parent in inNode[tailVar]:                    
                    if parent not in listS and len(inNode[parent]) > 0: # endogenous                        
                        listT.append(parent)
                    elif len(inNode[parent]) == 0:                    
                        if parent not in listU:                            
                            listU.append(parent)                             
                            resetFlag = True                

                if resetFlag:
                    tailIndex = 0
                    continue
            
            tailIndex += 1

        if v:
            print("--- debug end ---")
            print(f"list S: {listS}")
            print(f"list U: {listU}")
            print(f"list T: {listT}")
        
        return listS, listT, listU    

    def dSeparationChecker(node1: int, node2: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]]):
        """
        checks if two variables are d-separated given a DAG. Returns true if there is independency
        node1 and node2: the two nodes whose independency is being checked
        outNode        : all edges that leave the node
        inNode         : all edges that enter the node
        """

        visited: set[int] = set()
        findTarget = case1Solver.customDfs(node1, node2, outNode, inNode, visited, 2)
        return not findTarget

    def customDfs(currNode: int, targetNode: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]],
                  visited: set[int], lastDirection: int):
        """
        lastDirection: 0 means it entered the node, 1 means it left the node
        """
        visited.add(currNode)
        if currNode == targetNode:
            return True

        findTarget: bool = False
        for node in outNode[currNode]:
            if node not in visited:
                findTarget = case1Solver.customDfs(node, targetNode, outNode, inNode, visited, 0)
                if findTarget == True:
                    return True

        if lastDirection != 0:
            for node in inNode[currNode]:
                if node not in visited:
                    findTarget = case1Solver.customDfs(node, targetNode, outNode, inNode, visited, 1)        
                    if findTarget == True:
                        return True
        return False            

def itauTest():
    # Itau graph: 
    outNode = {0: [], 1: [0, 2], 2: [0], 3: [2], 4: [0, 1], 5: [2], 6: [3]}
    inNode =  {0: [1, 2, 4], 1: [4], 2: [1, 3, 5], 3: [6], 4: [], 5: [], 6: []}
    case1Solver.dSeparationChecker(node1=2, node2=2, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=2, node2=4, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=5, node2=4, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=6, node2=4, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=3, node2=4, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=1, node2=4, outNode=outNode, inNode=inNode)
    case1Solver.dSeparationChecker(node1=6, node2=2, outNode=outNode, inNode=inNode)
        
    # Example of compatible intervention: target 0 interveening on 1
    cCompList: list[latentAndCcomp] = []
    cCompList.append(latentAndCcomp(latent=4, nodes=[0, 1, 4]))
    cCompList.append(latentAndCcomp(latent=5, nodes=[2, 5]))
    cCompList.append(latentAndCcomp(latent=6, nodes=[3, 6]))

    cCompDict: dict[int, list[int]] = {}
    for el in cCompList:
        cCompDict[el.latent] = el.nodes
        pass

    cardinalities = {0: 2, 1: 2, 2: 2, 3: 2}
    indexToLabel = {0: "Y", 1: "T", 2: "D", 3: "E"}
    case1Solver.objetiveFunctionBuilder(latentIntervention=4, cComponentIntervention=[0, 1, 4], outNode=outNode, inNode=inNode,
                                        cCompDict=cCompDict, cardinalities=cardinalities,
                                        interventionVariable=1,interventionValue=0,targetVariable=0,targetValue=0,
                                        topoOrder=[3, 1, 2, 0],
                                        filepath="itau.csv",
                                        indexToLabel=indexToLabel,
                                        v=False)
    
def cycleCase():    
    # Nao funciona porque a funcao dSeparation nao esta lidando com ciclos
    outNode = {0: [1, 2], 1: [2, 4], 2: [], 3: [1], 4: [2, 3], 5: [5], 6: [3]}
    inNode =  {0: [], 1: [3], 2: [0, 1, 4], 3: [6], 4: [1, 5], 5: [], 6: []}    
        
    # Example of compatible intervention: target 2 interveening on 1
    case1Solver.findSuperTail(latent=0, cComponent=[0, 1, 2], outNode=outNode, inNode=inNode)

if __name__ == "__main__":    
    itauTest()
    #cycleCase()