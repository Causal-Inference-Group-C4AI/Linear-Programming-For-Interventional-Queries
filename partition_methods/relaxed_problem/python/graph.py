import networkx as nx
from causal_solver.SupertailFinder import Node

class Graph:
    def __init__(self, numberOfNodes: int, currNodes: list[int], visited: list[bool], cardinalities: dict[int, int],
                 parents: list[int], adj: list[list[int]], labelToIndex: dict[str, int], indexToLabel: dict[int, str],
                 dagComponents: list[list[int]], exogenous : list[int], endogenous : list[int], topologicalOrder: list[int], 
                 DAG: nx.digraph, cComponentToUnob: dict[int, int], graphNodes: list[Node]):

        self.numberOfNodes = numberOfNodes
        self.currNodes = currNodes
        self.visited = visited 
        self.cardinalities = cardinalities
        self.parents = parents
        self.adj = adj
        self.labelToIndex = labelToIndex
        self.indexToLabel = indexToLabel
        self.dagComponents = dagComponents
        self.endogenous = endogenous
        self.exogenous = exogenous
        self.topologicalOrder = topologicalOrder
        self.DAG = DAG
        self.cComponentToUnob = cComponentToUnob
        
        self.graphNodes = graphNodes


    def parse():
        numberOfNodes = int(input())
        numberOfEdges = int(input())
        
        labelToIndexEx: dict[str, int] = {} 
        indexToLabelEx: dict[int, str] = {} 
        adjEx: list[list[int]] = [[] for _ in range(numberOfNodes)]
        cardinalitiesEx = {}
        visited_ex = [False] * (numberOfNodes)
        parentsEx: list[list[int]] = [[] for _ in range(numberOfNodes)]
        endogenIndex : list[int] = []
        exogenIndex : list[int] = []
        

        for i in range(numberOfNodes):
            label, cardinality = input().split()
            cardinality = int(cardinality)
            labelToIndexEx[label] = i
            indexToLabelEx[i] = label
            cardinalitiesEx[i] = cardinality

        for _ in range(numberOfEdges):
            u, v = input().split()
            uIndex = labelToIndexEx[u]
            vIndex = labelToIndexEx[v]
            adjEx[uIndex].append(vIndex)
            parentsEx[vIndex].append(uIndex)


        inpDAG: nx.DiGraph = nx.DiGraph()
    
        for i in range(numberOfNodes):
            inpDAG.add_node(i)
    
        for parent, edge in enumerate(adjEx):
            if bool(edge):
               for ch in edge:
                   inpDAG.add_edge(parent, ch)
        
        order = list(nx.topological_sort(inpDAG))
        
        for i in range(numberOfNodes) :
        
             name_node = indexToLabelEx[i] 

             nx.relabel_nodes(inpDAG, {i : name_node}, copy=False)
       
        for i in range(numberOfNodes):
           
           if not (bool(parentsEx[i])):
               exogenIndex.append(i)
           else:
               endogenIndex.append(i)                

        graphNodes: list[Node] = [Node(latentParent=-1, parents=[], children=[]) for _ in range(numberOfNodes)]
        for node in range(numberOfNodes):
            if cardinalitiesEx[node] == 0:
                graphNodes[node] = Node(children=adjEx[node],parents=[],latentParent=None)
            else:
                latentParent = -1
                for nodeParent in parentsEx[node]:
                    if cardinalitiesEx[nodeParent] == 0:
                        latentParent = nodeParent
                        break
            
                if latentParent == -1:
                    print(f"PARSE ERROR: ALL OBSERVABLE VARIABLES SHOULD HAVE A LATENT PARENT, BUT {node} DOES NOT.")
                
                graphNodes[node] = Node(children=adjEx[node],parents=parentsEx[node],latentParent=latentParent)
            pass

        return Graph(numberOfNodes=numberOfNodes,currNodes=[], visited=visited_ex, cardinalities=cardinalitiesEx, parents=parentsEx, 
                    adj=adjEx, indexToLabel=indexToLabelEx, labelToIndex=labelToIndexEx, dagComponents=[], exogenous= exogenIndex,endogenous = endogenIndex, topologicalOrder= order, DAG= inpDAG, 
                    cComponentToUnob = {}, graphNodes=graphNodes)
    
    def dfs(self, node: int):        
        self.visited[node] = True
        self.currNodes.append(node)
        is_observable = self.cardinalities[node] > 1

        if not is_observable:
            for adj_node in self.adj[node]:
                if not self.visited[adj_node]:
                   self.dfs(adj_node)
        else:
            for parent_node in self.parents[node]:
                if not self.visited[parent_node] and self.cardinalities[parent_node] < 1:
                    self.dfs(parent_node)
    
    def find_cComponents(self):
        for i in range(1, self.numberOfNodes + 1):
            if not self.visited[i] and self.cardinalities[i] < 1:            
                self.currNodes.clear()
                self.dfs(i)
                self.dagComponents.append(self.currNodes[:])
                self.cComponentToUnob[len(self.dagComponents) - 1] = i
if __name__ == "__main__":
    graph: Graph = Graph.parse()
