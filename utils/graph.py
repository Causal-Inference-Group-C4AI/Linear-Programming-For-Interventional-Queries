import inspect
import sys
import networkx as nx
from causal_solver.MoralNode import MoralNode
from causal_solver.Node import Node

class Graph:
    def __init__(self, numberOfNodes: int, currNodes: list[int], visited: list[bool], cardinalities: dict[int, int],
                 parents: list[list[int]], adj: list[list[int]], labelToIndex: dict[str, int], indexToLabel: dict[int, str],
                 dagComponents: list[list[int]], exogenous : list[int], endogenous : list[int], topologicalOrder: list[int],
                 DAG: nx.digraph, cComponentToUnob: dict[int, int], graphNodes: list[Node],
                 moralGraphNodes: list[MoralNode]):

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
        self.moralGraphNodes = moralGraphNodes

    def parseTerminal():
        numberOfNodes = int(input())
        numberOfEdges = int(input())

        labelToIndex: dict[str, int] = {}; indexToLabel: dict[int, str] = {}
        adj: list[list[int]] = [[] for _ in range(numberOfNodes)]
        cardinalities: dict[int, int] = {}
        parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

        for i in range(numberOfNodes):
            label, cardinality = input().split()            
            if not any(char.isalpha() for char in label):                
                print("Error: The label must contain only alphabetic characters.")
                sys.exit(1)

            cardinality = int(cardinality)
            labelToIndex[label] = i
            indexToLabel[i] = label
            cardinalities[i] = cardinality

        for _ in range(numberOfEdges):
            u, v = input().split()
            uIndex = labelToIndex[u]
            vIndex = labelToIndex[v]
            adj[uIndex].append(vIndex)
            parents[vIndex].append(uIndex)

        return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents

    def parseInterface(nodesString: str, edgesString: str):
        nodesAndCardinalitiesList: list[str] = nodesString.split(',')
        numberOfNodes = len(nodesAndCardinalitiesList)

        cardinalities: dict[int, int] = {}; labelToIndex: dict[str, int] = {}; indexToLabel: dict[int, str] = {}
        adj    : list[list[int]] = [[] for _ in range(numberOfNodes)]
        parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

        for i, element in enumerate(nodesAndCardinalitiesList):
            auxPair = element.split('=')
            cardinalities[i] = auxPair[1]
            labelToIndex[auxPair[0]] = i
            indexToLabel[i] = auxPair[0]
            cardinalities[i] = int(auxPair[1])

        for element in edgesString.split(','):            
            elAux = element.split('->')            
            fatherIndex = labelToIndex[elAux[0]] 
            sonIndex = labelToIndex[elAux[1]]
            adj[fatherIndex].append(sonIndex)
            parents[sonIndex].append(fatherIndex)

        return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents

    def parse(fromInterface=False, nodesString="", edgesString=""):
        if fromInterface:            
            auxTuple = Graph.parseInterface(nodesString, edgesString)
        else:
            auxTuple = Graph.parseTerminal()

        numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents = auxTuple

        inpDAG: nx.DiGraph = nx.DiGraph()
        for i in range(numberOfNodes):
            inpDAG.add_node(i)
    
        for parent, edge in enumerate(adj):
            if bool(edge):
               for ch in edge:
                   inpDAG.add_edge(parent, ch)
        
        order = list(nx.topological_sort(inpDAG))
        
        for i in range(numberOfNodes) :
        
             name_node = indexToLabel[i] 

             nx.relabel_nodes(inpDAG, {i : name_node}, copy=False)

        endogenIndex : list[int] = []; exogenIndex : list[int] = []
        for i in range(numberOfNodes):
           if not (bool(parents[i])):
               exogenIndex.append(i)
           else:
               endogenIndex.append(i)                

        graphNodes: list[Node] = [Node(latentParent=-1, parents=[], children=[]) for _ in range(numberOfNodes)]
        for node in range(numberOfNodes):
            if cardinalities[node] == 0:
                graphNodes[node] = Node(children=adj[node],parents=[],latentParent=None)
            else:
                latentParent = -1
                for nodeParent in parents[node]:
                    if cardinalities[nodeParent] == 0:
                        latentParent = nodeParent
                        break
            
                if latentParent == -1:
                    print(f"PARSE ERROR: ALL OBSERVABLE VARIABLES SHOULD HAVE A LATENT PARENT, BUT {node} DOES NOT.")
                
                graphNodes[node] = Node(children=adj[node],parents=parents[node],latentParent=latentParent)
            pass

        return Graph(numberOfNodes=numberOfNodes,currNodes=[], visited=[False] * (numberOfNodes), cardinalities=cardinalities, parents=parents,
                    adj=adj, indexToLabel=indexToLabel, labelToIndex=labelToIndex, dagComponents=[], exogenous= exogenIndex,endogenous = endogenIndex, topologicalOrder= order, DAG= inpDAG,
                    cComponentToUnob = {}, graphNodes=graphNodes, moralGraphNodes=[])
    
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
    
    def base_dfs(self, node: int):
        self.visited[node] = True
        self.currNodes.append(node)

        for adj_node in self.graphNodes[node].children:
            if not self.visited[adj_node]:
                self.dfs(adj_node)
    
    def find_cComponents(self):
        for i in range(1, self.numberOfNodes + 1):
            if not self.visited[i] and self.cardinalities[i] < 1:            
                self.currNodes.clear()
                self.dfs(i)
                self.dagComponents.append(self.currNodes[:])
                self.cComponentToUnob[len(self.dagComponents) - 1] = i

    def is_descendant(self, ancester, descendant):
        for i in range(len(self.visited)):
            self.visited[i] = False        

        self.currNodes = []
        self.base_dfs(node=ancester)

        return self.visited[descendant]
    
    def build_moral(self, consideredNodes: list[int], flag: bool, intervention: int):
        """
        Builds the moral graph, considering only part of the nodes.
        flag: if true, the outgoing edges of the intervention should not be considered.
        """

        self.moralGraphNodes = [MoralNode(adjacent=[]) for _ in range(self.numberOfNodes)]
        for node in range(self.numberOfNodes):
            if node in consideredNodes:
                for parent in self.graphNodes[node].parents:
                    if flag and (parent == intervention):
                            continue
                    for parent2 in self.graphNodes[node].parents:
                        if flag and (parent2 == intervention):
                            continue
                        if node < parent:
                            if node in consideredNodes and parent in consideredNodes:
                                self.moralGraphNodes[node].adjacent.append(parent)
                                self.moralGraphNodes[parent].adjacent.append(node)
                        if node < parent2:
                            if node in consideredNodes and parent2 in consideredNodes:
                                self.moralGraphNodes[node].adjacent.append(parent2)
                                self.moralGraphNodes[parent2].adjacent.append(node)
                        if parent < parent2:
                            if (parent in consideredNodes and parent2 in consideredNodes):
                                self.moralGraphNodes[parent].adjacent.append(parent2)
                                self.moralGraphNodes[parent2].adjacent.append(parent)

    def find_ancesters(self, node: int):
        self.currNodes.clear()
        self.visited =  [False] * self.numberOfNodes

        self.dfs_ancester(node)
        ancesters: list[int] = []
        for i in range(0,self.numberOfNodes):
            if self.visited[i]:
                ancesters.append(i)

        return ancesters

    def dfs_ancester(self, node):
        self.visited[node] = True

        for parent in self.graphNodes[node].parents:
            if not self.visited[parent]:
                self.dfs_ancester(parent)
    
    def independency_moral(self, node1: int, node2: int):
        self.visited = [False] * self.numberOfNodes
        self.dfs_moral(node1)
        
        return not self.visited[node2]

    def dfs_moral(self, node):
        self.visited[node] = True

        for adj in self.moralGraphNodes[node].adjacent:
            if not self.visited[adj]:
                self.dfs_moral(node=adj)

if __name__ == "__main__":
    graph: Graph = Graph.parse()
