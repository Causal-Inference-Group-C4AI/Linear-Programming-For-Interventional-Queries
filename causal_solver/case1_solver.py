class case1Solver:                
    """
    Determines the a "supertail" T of a set of endogenous variables V associated to a set of latent variables
    U such that T and U fully determine V and T and U are indepedent. We consider that the independency hypothesis
    are already inserted in the graph and assume d-separation to be its equivalent.
    The case1 is when both the variable under intervention as well as the target variable are in the same c-component
    """
    
    def findSuperTail(latent: int, cComponent: int, outNode: dict[int, list[int]], inNode: dict[int, list[int]]):
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

        print("--- Debug initialization ---")
        print(f"List U: {listU}")
        print(f"List S: {listS}")
        print(f"List T: {listT}")

        
        # Remember to come back to the beginning of the list if some new latent is added!
        tailIndex = 0
        while tailIndex < len(listT):
            tailVar = listT[tailIndex]
            # Check independency with the latent variables!        
            print(f"Check indep for tail var: {tailVar}")
            print(f"--- check each latent ---")
            tailIndepU = True
            for latentVar in listU:
                print(f"Test latent: {latentVar}")
                independency = case1Solver.dSeparationChecker(tailVar, latentVar, outNode, inNode)
                if not independency:
                    print("Not independent!")
                    tailIndepU = False
                    break
            
            if not tailIndepU:
                print(f"Remove node {tailVar} from tail and add to S")
                listT.remove(tailVar)                
                listS.append(tailVar)
                
                resetFlag: bool = False                
                print(f"Check parents of node {tailVar}")
                for parent in inNode[tailVar]:                    
                    if parent not in listS and len(inNode[parent]) > 0: # endogenous
                        print(f"Add to tail the endogenous: {parent}")
                        listT.append(parent)
                    elif len(inNode[parent]) == 0:
                        print(f"Add latent: {parent}")
                        if parent not in listU:                            
                            listU.append(parent)                             
                            resetFlag = True                

                if resetFlag:
                    tailIndex = 0
                    continue
            
            tailIndex += 1

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
        print(f"Are nodes {node1} and {node2} independent? {not findTarget}")
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
    case1Solver.findSuperTail(latent=4, cComponent=[0, 1, 4], outNode=outNode, inNode=inNode)
    
def cycleCase():    
    # Nao funciona porque a funcao dSeparation nao esta lidando com ciclos
    outNode = {0: [1, 2], 1: [2, 4], 2: [], 3: [1], 4: [2, 3], 5: [5], 6: [3]}
    inNode =  {0: [], 1: [3], 2: [0, 1, 4], 3: [6], 4: [1, 5], 5: [], 6: []}    
        
    # Example of compatible intervention: target 2 interveening on 1
    case1Solver.findSuperTail(latent=0, cComponent=[0, 1, 2], outNode=outNode, inNode=inNode)

if __name__ == "__main__":    
    itauTest()
    #cycleCase()