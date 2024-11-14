import networkx as nx
class Graph:    
    def __init__(self, num_nodes: int, curr_nodes: list[int], visited: list[bool], cardinalities: list[int], 
                 parents: list[int], adj: list[list[int]], label_to_index: dict[str, int], index_to_label: dict[int, str],
                 dag_components: list[list[int]], exogenous : list[int], endogenous : list[int], topological_order: list[int], DAG: nx.digraph, cComponent_to_Unob: dict[int, int]):
        self.num_nodes = num_nodes
        self.curr_nodes = curr_nodes
        self.visited = visited 
        self.cardinalities = cardinalities
        self.parents = parents
        self.adj = adj
        self.label_to_index = label_to_index
        self.index_to_label = index_to_label
        self.dag_components = dag_components
        self.endogenous = endogenous
        self.exogenous = exogenous
        self.topological_order = topological_order
        self.DAG = DAG
        self.cComponent_to_unob = cComponent_to_Unob
    def parse():
        num_nodes = int(input())
        num_edges = int(input())
        
        label_to_index_ex: dict[str, int] = {} 
        index_to_label_ex: dict[int, str] = {} 
        adj_ex = [[] for _ in range(num_nodes + 1)]
        cardinalities_ex = [0] * (num_nodes + 1)
        visited_ex = [False] * (num_nodes + 1)
        parents_ex = [[] for _ in range(num_nodes + 1)]
        endogenIndex : list[int] = []
        exogenIndex : list[int] = []
        for i in range(1, num_nodes + 1):
            label, cardinality = input().split()
            cardinality = int(cardinality)
            label_to_index_ex[label] = i
            index_to_label_ex[i] = label
            cardinalities_ex[i] = cardinality

        for _ in range(num_edges):
            u, v = input().split()
            u_index = label_to_index_ex[u]
            v_index = label_to_index_ex[v]
            adj_ex[u_index].append(v_index)
            parents_ex[v_index].append(u_index)
        inpDAG: nx.DiGraph = nx.DiGraph()
    
        for i in range(1, num_nodes+1):
            inpDAG.add_node(i)
    
        for parent, edge in enumerate(adj_ex):
            if bool(edge):
               for ch in edge:
                   inpDAG.add_edge(parent, ch)
        
        order = list(nx.topological_sort(inpDAG))
        
        for i in range(1, num_nodes + 1) :
        
             name_node = index_to_label_ex[i] 

             nx.relabel_nodes(inpDAG, {i : name_node}, copy=False)
       
        for i in range(1, num_nodes + 1):
           
           if not (bool(parents_ex[i])) :
               exogenIndex.append(i)
           else :
               endogenIndex.append(i)
        
        return Graph(num_nodes=num_nodes,curr_nodes=[], visited=visited_ex, cardinalities=cardinalities_ex, parents=parents_ex, 
                    adj=adj_ex, index_to_label=index_to_label_ex, label_to_index=label_to_index_ex, dag_components=[], exogenous= exogenIndex,endogenous = endogenIndex, topological_order= order, DAG= inpDAG, cComponent_to_Unob = {})
    
    def dfs(self, node: int):        
        self.visited[node] = True
        self.curr_nodes.append(node)
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
        for i in range(1, self.num_nodes + 1):
            if not self.visited[i] and self.cardinalities[i] < 1:            
                self.curr_nodes.clear()
                self.dfs(i)
                self.dag_components.append(self.curr_nodes[:])
                self.cComponent_to_unob[len(self.dag_components) - 1] = i
if __name__ == "__main__":
    graph: Graph = Graph.parse()
