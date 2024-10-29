def process_test_data(file_path):
    test = {}

    with open(file_path, 'r') as file:
        # First line is the number of tests
        test['num_nodes'] = int(file.readline().strip())
        test['num_edges'] = int(file.readline().strip())
        test['nodes'] = []
        test['node_cardinality'] = []
        for _ in range(test['num_nodes']):
            node_cardinality_tuple = file.readline().strip().split(' ')
            test['nodes'].append(node_cardinality_tuple[0])
            test['node_cardinality'].append(int(node_cardinality_tuple[1]))
        test['edges'] = []
        for _ in range(test['num_edges']):
            nodes = file.readline().strip().split(' ')
            test['edges'].append((nodes[0], nodes[1]))
    return test

def file_parser(file_path):
    test = process_test_data(file_path)
    num_nodes = test['num_nodes']
    num_edges = test['num_edges']
    
    label_to_index_ex: dict[str, int] = {} 
    index_to_label_ex: dict[int, str] = {} 
    adj_ex = [[] for _ in range(num_nodes + 1)]
    cardinalities_ex = [0] * (num_nodes + 1)
    visited_ex = [False] * (num_nodes + 1)
    parents_ex = [[] for _ in range(num_nodes + 1)]
    endogenIndex : list[int] = []
    exogenIndex : list[int] = []
    for i in range(num_nodes):
        label = test['nodes'][i]
        cardinality = test['node_cardinality'][i]
        label_to_index_ex[label] = i + 1
        index_to_label_ex[i + 1] = label
        cardinalities_ex[i + 1] = cardinality

    for i in range(num_edges):
        u = test['edges'][i][0]
        v = test['edges'][i][1]
        u_index = label_to_index_ex[u]
        v_index = label_to_index_ex[v]
        adj_ex[u_index].append(v_index)
        parents_ex[v_index].append(u_index)
    
    for i in range(num_nodes):
        
        if not (bool(parents_ex[i+1])):
            exogenIndex.append(i+1)
        else :
            endogenIndex.append(i+1)
    
    return Graph(num_nodes=num_nodes,curr_nodes=[], visited=visited_ex, cardinalities=cardinalities_ex, parents=parents_ex, 
                adj=adj_ex, index_to_label=index_to_label_ex, label_to_index=label_to_index_ex, dag_components=[], exogenous= exogenIndex,endogenous = endogenIndex)

class Graph:    
    def __init__(self, num_nodes: int, curr_nodes: list[int], visited: list[bool], cardinalities: list[int], 
                 parents: list[int], adj: list[list[int]], label_to_index: dict[str, int], index_to_label: dict[int, str],
                 dag_components: list[list[int]], exogenous : list[int], endogenous : list[int]):
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

    def parse(file_path=None):
        if file_path is not None:
            return file_parser(file_path)

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
        
        for i in range(1, num_nodes + 1):
           
           if not (bool(parents_ex[i])) :
               exogenIndex.append(i)
           else :
               endogenIndex.append(i)
        
        return Graph(num_nodes=num_nodes,curr_nodes=[], visited=visited_ex, cardinalities=cardinalities_ex, parents=parents_ex, 
                    adj=adj_ex, index_to_label=index_to_label_ex, label_to_index=label_to_index_ex, dag_components=[], exogenous= exogenIndex,endogenous = endogenIndex)