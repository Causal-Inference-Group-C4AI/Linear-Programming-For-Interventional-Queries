import sys

import networkx as nx

from causal_usp_icti.graph.moral_node import MoralNode
from causal_usp_icti.graph.node import Node


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

    def parse_terminal():
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

    def parse_interface(nodesString: str, edgesString: str):
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
            auxTuple = Graph.parse_interface(nodesString, edgesString)
        else:
            auxTuple = Graph.parse_terminal()

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

        graphNodes: list[Node] = [Node(latentParent=-1, parents=[], children=[], isLatent=False) for _ in range(numberOfNodes)]
        for node in range(numberOfNodes):
            if cardinalities[node] == 0:
                graphNodes[node] = Node(children=adj[node],parents=[],latentParent=None,isLatent=True)
            else:
                latentParent = -1
                for nodeParent in parents[node]:
                    if cardinalities[nodeParent] == 0:
                        latentParent = nodeParent
                        break

                if latentParent == -1:
                    print(f"PARSE ERROR: ALL OBSERVABLE VARIABLES SHOULD HAVE A LATENT PARENT, BUT {node} DOES NOT.")

                graphNodes[node] = Node(children=adj[node],parents=parents[node],latentParent=latentParent,isLatent=False)
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
    
    def find_cComponents(self):
        for i in range(self.numberOfNodes):
            if not self.visited[i] and self.cardinalities[i] < 1:            
                self.currNodes.clear()
                self.dfs(i)
                self.dagComponents.append(self.currNodes[:])
                self.cComponentToUnob[len(self.dagComponents) - 1] = i
    
    def base_dfs(self, node: int):
        self.visited[node] = True

        for adj_node in self.graphNodes[node].children:
            if not self.visited[adj_node]:                
                self.base_dfs(adj_node)

    def is_descendant(self, ancestor, descendant):        
        for i in range(len(self.visited)):
            self.visited[i] = False        
                
        self.base_dfs(node=ancestor)        

        return self.visited[descendant]
    
    def build_moral(self, consideredNodes: list[int], conditionedNodes: list[int], flag=False, intervention=-1):
        """
        Builds the moral graph, considering only part of the nodes.
        flag: if true, the outgoing edges of the intervention should not be considered.
        """
        self.moralGraphNodes = [MoralNode(adjacent=[]) for _ in range(self.numberOfNodes)]
        for node in range(self.numberOfNodes):
            if node not in consideredNodes: 
                continue
            
            if node in conditionedNodes:                
                for parent1 in self.graphNodes[node].parents:
                    if flag and parent1 == intervention: continue
                    for parent2 in self.graphNodes[node].parents:
                        if flag and parent2 == intervention: continue
                        
                        if (parent1 in conditionedNodes and parent2 in consideredNodes):
                            if parent2 not in self.moralGraphNodes[parent1].adjacent:
                                self.moralGraphNodes[parent1].adjacent.append(parent2)
                            if parent1 not in self.moralGraphNodes[parent2].adjacent:
                                self.moralGraphNodes[parent2].adjacent.append(parent1)                
            else:
                if (flag and node == intervention): continue
                
                for ch in self.graphNodes[node].children:                    
                    if ch in consideredNodes and ch not in conditionedNodes:
                        if node not in self.moralGraphNodes[ch].adjacent:
                            self.moralGraphNodes[ch].adjacent.append(node)
                        if ch not in self.moralGraphNodes[node].adjacent:
                            self.moralGraphNodes[node].adjacent.append(ch)
                
    def find_ancestors(self, node: int):
        self.currNodes.clear()
        self.visited =  [False] * self.numberOfNodes

        self.dfs_ancestor(node)
        ancestors: list[int] = []
        for i in range(0,self.numberOfNodes):
            if self.visited[i]:
                ancestors.append(i)

        return ancestors

    def dfs_ancestor(self, node):
        self.visited[node] = True

        for parent in self.graphNodes[node].parents:
            if not self.visited[parent]:
                self.dfs_ancestor(parent)
    
    def independency_moral(self, node1: int, node2: int):
        self.visited = [False] * self.numberOfNodes
        self.dfs_moral(node1)
        
        return not self.visited[node2]

    def dfs_moral(self, node):
        self.visited[node] = True

        for adj in self.moralGraphNodes[node].adjacent:
            if not self.visited[adj]:
                self.dfs_moral(node=adj)

def parse_file(file_path: str):
    with open(file_path, 'r') as file:

        numberOfNodes = file.readline().strip()
        numberOfEdges = file.readline().strip()

        numberOfNodes = int(numberOfNodes)
        numberOfEdges = int(numberOfEdges)

        labelToIndex: dict[str, int] = {}; indexToLabel: dict[int, str] = {}
        adj: list[list[int]] = [[] for _ in range(numberOfNodes)]
        cardinalities: dict[int, int] = {}
        parents: list[list[int]] = [[] for _ in range(numberOfNodes)]

        for i in range(numberOfNodes):
            label, cardinality = file.readline().strip().split()
            
            cardinality = int(cardinality)
            labelToIndex[label] = i
            indexToLabel[i] = label
            cardinalities[i] = cardinality

        for _ in range(numberOfEdges):
            u, v = file.readline().strip().split()
            uIndex = labelToIndex[u]
            vIndex = labelToIndex[v]
            adj[uIndex].append(vIndex)
            parents[vIndex].append(uIndex)

        return numberOfNodes, labelToIndex, indexToLabel, adj, cardinalities, parents

def parse():
    auxTuple = Graph.parse_file()
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

    graphNodes: list[Node] = [Node(latentParent=-1, parents=[], children=[], isLatent=False) for _ in range(numberOfNodes)]
    for node in range(numberOfNodes):
        if cardinalities[node] == 0:
            graphNodes[node] = Node(children=adj[node],parents=[],latentParent=None,isLatent=True)
        else:
            latentParent = -1
            for nodeParent in parents[node]:
                if cardinalities[nodeParent] == 0:
                    latentParent = nodeParent
                    break
        
            if latentParent == -1:
                print(f"PARSE ERROR: ALL OBSERVABLE VARIABLES SHOULD HAVE A LATENT PARENT, BUT {node} DOES NOT.")
            
            graphNodes[node] = Node(children=adj[node],parents=parents[node],latentParent=latentParent,isLatent=False)
        pass

    return Graph(numberOfNodes=numberOfNodes,currNodes=[], visited=[False] * (numberOfNodes), cardinalities=cardinalities, parents=parents,
                adj=adj, indexToLabel=indexToLabel, labelToIndex=labelToIndex, dagComponents=[], exogenous= exogenIndex,endogenous = endogenIndex, topologicalOrder= order, DAG= inpDAG,
                cComponentToUnob = {}, graphNodes=graphNodes, moralGraphNodes=[])

if __name__ == "__main__":
    graph: Graph = Graph.parse()
