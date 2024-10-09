class Graph:    
    def __init__(self, num_nodes: int, curr_nodes: list[int], visited: list[bool], cardinalities: list[int], 
                 parents: list[int], adj: list[list[int]], label_to_index: dict[int, str], index_to_label: dict[str, int],
                 dag_components: list[list[int]]):
        self.num_nodes = num_nodes
        self.curr_nodes = curr_nodes
        self.visited = visited 
        self.cardinalities = cardinalities
        self.parents = parents
        self.adj = adj
        self.label_to_index = label_to_index
        self.index_to_label = index_to_label
        self.dag_components = dag_components

    def parse():
        num_nodes = int(input())
        num_edges = int(input())
        
        label_to_index_ex: dict[str, int] = {} 
        index_to_label_ex: dict[int, str] = {} 
        adj_ex = [[] for _ in range(num_nodes + 1)]
        cardinalities_ex = [0] * (num_nodes + 1)
        visited_ex = [False] * (num_nodes + 1)
        parents_ex = [[] for _ in range(num_nodes + 1)]

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
        
        return Graph(num_nodes=num_nodes,curr_nodes=[], visited=visited_ex, cardinalities=cardinalities_ex, parents=parents_ex, 
                    adj=adj_ex, index_to_label=index_to_label_ex, label_to_index=label_to_index_ex, dag_components=[])