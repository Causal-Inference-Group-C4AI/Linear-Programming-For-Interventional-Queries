from collections import namedtuple
from helper import helper

latentAndCcomp = namedtuple('latentAndCcomp', ['latent', 'nodes'])
dictAndIndex   = namedtuple('dictAndIndex', ['mechanisms', 'index'])
equationsObject = namedtuple('equationsObject', ['probability', 'dictionary'])

class case1Solver:
    """
    Determines the a "supertail" T of a set of endogenous variables V associated to a set of latent variables
    U such that T and U fully determine V and T and U are indepedent. We consider that the independency hypothesis
    are already inserted in the graph and assume d-separation to be its equivalent.
    The case1 is when both the variable under intervention as well as the target variable are in the same c-component
    """
    def equationsGenerator(mechanismDictsList: list[list[dictAndIndex]], setT: list[int], setS: list[int], setU: list[int],
                            cardinalities: dict[int,int], parents: dict[int, list[int]], topoOrder: list[int], indexToLabel: dict[int, str],
                            filepath: str):
        """
        Given the supertail (set T), the endogenous variables S (set S) and the latent variables U (set U), it generates the equations:
        p = P(S=s|T=t) = Sum{P(U=u)*1(U=u,T=t -> S=s)}. Hence, each combination of latents has a coefficient, which
        can be 0 or 1 only.

        mechanismDictsList: a list in which each element corresponds to an enumeration of the mechanisms (states) of a latent variable.
        setT: supertail
        setS: set of endogenous variables determined by the supertail
        cardinalities: dict with the cardinalities of the variables in T and S.
        parents: equal to nodesIn, and contains the set of all parents of an endogenous variable
        topoOrder: a topological order to run through S
        endoIndexToLabel: convert from index of a variable in S to the label used in a CSV file
        precision: defines how many decimals the calculated probability should have
        """
        df = helper.fetchCsv(filepath)

        cardinalitiesTail: dict[int, int] = {}; cardinalitiesEndo: dict[int, int] = {}
        for key in cardinalities:
            if key in setT:
                cardinalitiesTail[key] = cardinalities[key]
            elif key in setS:
                cardinalitiesEndo[key] = cardinalities[key]

        tailSpace: list[list[int]] = helper.helperGenerateSpaces(nodes=setT, cardinalities=cardinalitiesTail)
        tailCombinations = helper.generateCrossProducts(tailSpace)
        endoSpace = helper.helperGenerateSpaces(nodes=setS,  cardinalities=cardinalitiesEndo)
        endoCombinations = helper.generateCrossProducts(endoSpace)
        latentCombinations = helper.generateCrossProducts(mechanismDictsList)

        # Lista de equacoes do tipo:
        # p = ai * U1 * U2...*Un => tome um dicionário para cada linha (equacao)
        # em que o ai eh indexado da mesma forma que na funcao objetivo.
        # Cada linha precisa de um dicionario e de um valor.
        equations: list[equationsObject] = []

        for tailRealization in tailCombinations:
            tailRealizationDict = dict(zip(setT, tailRealization))
            for endoRealization in endoCombinations:
                endoRealizationDict = dict(zip(setS, endoRealization))
                probability: float = helper.findConditionalProbability(dataFrame=df,indexToLabel=indexToLabel,targetRealization=tailRealizationDict,
                                                  conditionRealization=endoRealizationDict)
                
                coefficientsDict: dict[str,int] = {}
                for latentRealization in latentCombinations:                    
                    isCompatible: bool = case1Solver.checkRealization(mechanismDictsList=latentRealization,
                                                parents=parents,
                                                topoOrder=topoOrder,
                                                tailValues=tailRealizationDict,
                                                latentVariables=setU,
                                                expectedRealizations=endoRealizationDict,                                                     
                                                )
                    indexer: str = ""
                    for latentMechanism in latentRealization:                
                        indexer += f"{latentMechanism.index},"
                    indexer = indexer.rstrip(',')
                    
                    coefficientsDict[indexer] = int(isCompatible)                             
                    
                equations.append(equationsObject(probability, coefficientsDict))
                
        # TODO: Union of U states must have probability one        

        return equations
    
    def objectiveFunctionBuilder(latentIntervention: int, cComponentIntervention: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]],
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
        dataFrame = helper.fetchCsv(filepath)

        listS, listT, listU = case1Solver.findSuperTail(latentIntervention, cComponentIntervention, outNode, inNode, False)
        # Remove nodes not in S from topoOrder AND the interventionNode:
        if interventionVariable in topoOrder:
            topoOrder.remove(interventionVariable)
        for node in topoOrder:
            if node not in listS:
                topoOrder.remove(node) 

        if v:
            print(f"Debug list S: {listS}")
            print(f"Debug list U: {listU}")
            print(f"Debug list T: {listT}")
                    
        mechanismDictsList: list[list[dictAndIndex]] = [] # Same order as in list U
        for latentVariable in listU:        
            endogenousNodes = cCompDict[latentVariable]
            if latentVariable in endogenousNodes:
                endogenousNodes.remove(latentVariable)
                        
            _, _, mechanismDicts = helper.mechanisms_generator(latentNode=latentVariable,endogenousNodes=endogenousNodes,
                                             cardinalities=cardinalities,parentsDict=inNode,v=False)
            
            # print(f"Debug mechanisms: {mechanismDicts}")
            mechanismIndexDict: list[dictAndIndex] = []
            for index, mechanismDict in enumerate(mechanismDicts):
                mechanismIndexDict.append(dictAndIndex(mechanismDict, index))
            
            mechanismDictsList.append(mechanismIndexDict)
                
        # Generate all the tail states        
        tailVarSpaces: list[list[int]] = helper.helperGenerateSpaces(listT, cardinalities)
        
        # Generate a cross product between all tail states AND all mechanisms (latent variable states)
        tailCombinations = helper.generateCrossProducts(tailVarSpaces) # the order is the same as in list T.
        latentCombinations = helper.generateCrossProducts(mechanismDictsList)
                
        if v:
            print("-- debug: tailCombinations --")
            for i, tailCombination in enumerate(tailCombinations):            
                print(f"{i}) {tailCombination}") 

            print("-- debug: latentCombinations --")
            for i, latentCombination in enumerate(latentCombinations):            
                print(f"latent combination {i}) {latentCombination}") 
        
        objectiveFunction: dict[str, int] = { } # Key = indexer (from array to str concatenated) and value = coefficient ai
        # F = sum(Prod(P(Uk)) * P(T=t) * 1(T=t,U=u => Y=y)) hence ai = P(T=t) iff 1() = 1 and 0 c.c
        for i, latentCombination in enumerate(latentCombinations):
            totalProbability: float = 0.0
            if v:
                print("---- START LATENT COMBINATION: ----")
                print(f"{latentCombination}")
            indexer: str = ""
            for latentMechanism in latentCombination:                
                indexer += f"{latentMechanism.index},"
            indexer = indexer.rstrip(',')

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
                                             latentVariables=listU,
                                             expectedRealizations={targetVariable: targetValue},
                                             interventionVariable=interventionVariable,
                                             interventionValue=interventionValue,
                                             )
                if isCompatible:  
                    empiricalProbability = helper.findProbability(dataFrame, indexToLabel, tailValues, False)
                    totalProbability += empiricalProbability

            if True:
                print(f"Debug: key = {indexer} and value = {totalProbability}")
            objectiveFunction[indexer] = totalProbability             

        return objectiveFunction            
    
    def checkRealization(mechanismDictsList: list[dict[str, int]], parents: dict[int, list[int]], topoOrder: list[int],
                tailValues: dict[int, int], latentVariables: list[int], expectedRealizations: dict[int, int],
                interventionVariable=-1, interventionValue=-1):
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
            if (node in expectedRealizations) and (computedNodes[node] != expectedRealizations[node]):
                return False

        return True

    def findSuperTail(latent: int, cComponent: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]], v: bool):
        """
        Given a graph, the node under intervention and the target node, it computes the supertail T and the set of latent
        variables U such that T and U are independent
        """        
        listU: list[int] = [latent] # Latent variables to be taken in account
        listT: list[int] = [] # 
        listS: list[int] = []
        
        for node in cComponent: # Need to complete this procedure before the next
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
                    if parent not in listS and len(inNode[parent]) > 0:
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
    case1Solver.objectiveFunctionBuilder(latentIntervention=4, cComponentIntervention=[0, 1, 4], outNode=outNode, inNode=inNode,
                                        cCompDict=cCompDict, cardinalities=cardinalities,
                                        interventionVariable=1,interventionValue=0,targetVariable=0,targetValue=0,
                                        topoOrder=[3, 1, 2, 0],
                                        filepath="itau.csv",
                                        indexToLabel=indexToLabel,
                                        v=False)
    
if __name__ == "__main__":    
    itauTest()
    #cycleCase()