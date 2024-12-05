from dataclasses import dataclass

@dataclass
class Node:
    children    : list[int]
    parents     : list[int]
    latentParent: int

class SupertailFinder:
    """
    Finds the supertail T given a DAG and an intervention (target and intervention variables)
    """
    def findSuperTail(node1: int, node2: int, graphNodes: list[Node]):
        """
        Given a graph, the node under intervention and the target node, it computes the supertail T and the set of latent
        variables U such that T and U are independent.
        """
        setS: set[int] = set([node1, node2])
        setU: set[int] = set([graphNodes[node1].latentParent, graphNodes[node2].latentParent])
        setT: set[int] = set()
        
        for node in setS:
            for parentNode in graphNodes[node].parents:
                if (parentNode not in setU) and (parentNode not in setS):
                    setT.add(parentNode)
        
        print(f"Init: setS: {setS}; setU: {setU}; setT: {setT}")

        independencyCondition = False
        while not independencyCondition:
            independencyCondition = True
            for supertailVar in setT:
                if not SupertailFinder.areDSeparated(node=supertailVar, targetNodes=setU, graphNodes=graphNodes):                    
                    independencyCondition = False
                    setT.remove(supertailVar)
                    setU.add(graphNodes[supertailVar].latentParent)
                    setS.add(supertailVar)
                    setT.update(set(graphNodes[supertailVar].parents) - setS.union(setU))                    
                    break
                
        return setS, setT, setU

    def areDSeparated(node: int, targetNodes: set[int], graphNodes: list[Node]):
        """
        checks if a node is d-separated from a set of targetNodes in a given a DAG. Returns true if there is independency
        between then node and any in the set.            
        """
        
        visited: set[int] = set()        
        SupertailFinder.customDfs(node, graphNodes, visited, 2)

        return 1 if len(visited.intersection(targetNodes)) == 0 else 0            

    def customDfs(currNode: int, graphNodes: list[Node], visited: set[int], lastDirection: int):
        """
        lastDirection: 0 means it entered the node, 1 means it left the node
        """
        visited.add(currNode)
        
        for node in graphNodes[currNode].children:
            if node not in visited:
                SupertailFinder.customDfs(node, graphNodes, visited, 0)                

        if lastDirection != 0:
            for node in (graphNodes[currNode].parents):
                if node not in visited:
                    SupertailFinder.customDfs(node, graphNodes, visited, 1)

        return False

def testDseparation():
    graphNodes = [Node(children=[], latentParent=4, parents=[1, 2, 4]),
                  Node(children=[0, 2], latentParent=4, parents=[4]),
                  Node(children=[0], latentParent=5, parents=[1, 3, 5]),
                  Node(children=[2], latentParent=6, parents=[6]),
                  Node(children=[0, 1], latentParent=[], parents=[]),
                  Node(children=[2], latentParent=[], parents=[]),
                  Node(children=[3], latentParent=[], parents=[])
                  ]
    
    tests: list[bool] = [SupertailFinder.areDSeparated(node=1, targetNodes={2}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=2, targetNodes={4}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=5, targetNodes={4}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=6, targetNodes={4}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=3, targetNodes={4}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=1, targetNodes={4}, graphNodes=graphNodes),
                        SupertailFinder.areDSeparated(node=6, targetNodes={2}, graphNodes=graphNodes)
                        ]
    expectedResults = [0, 0, 1, 1, 1, 0, 0]    

    for i in range(len(tests)):
        if tests[i] != expectedResults[i]:
            print(f"ASSERTION ERROR IN TEST {i + 1}")

def main():
    testDseparation()

if __name__ == "__main__":
    main() 
 