import math

adj = []  # 1-indexed
parents = []  # parents of each node (dual of adj)
label_to_index: dict[str, int] = {}  # Also 1-indexed
index_to_label: dict[int, str] = {}  # debugging
cardinalities = []  # <= 1 implies unknown
visited = []
curr_component = 0
curr_nodes = []

class CComponent:
    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

dag_components = []

def debug(num_nodes):
    print("debug indexToLabel")
    for index, label in index_to_label.items():
        print(f"index {index} label {label}")

    print("debug labelToIndex")
    for label, index in label_to_index.items():
        print(f"label {label} index {index}")

    print("Latent variables: \n")
    for i in range(1, num_nodes + 1):
        if cardinalities[i] < 1:
            print(f"latent var {i} with label {index_to_label[i]}")

    print("debugging graph:\n")
    for i in range(1, num_nodes + 1):
        print(f"Edges from {index_to_label[i]}")
        for el in adj[i]:
            print(index_to_label[el], end=" ")
        print()

def dfs(node):
    visited[node] = True
    curr_nodes.append(node)
    is_observable = cardinalities[node] > 1

    if not is_observable:
        for adj_node in adj[node]:
            if not visited[adj_node]:
                dfs(adj_node)
    else:
        for parent_node in parents[node]:
            if not visited[parent_node] and cardinalities[parent_node] < 1:
                dfs(parent_node)

def bound_for_canonical_partitions():
    for i, component in enumerate(dag_components):
        canonical_partition = 1
        for node in component.nodes:
            if cardinalities[node] > 1:
                base = cardinalities[node]
                exponent = 1
                for parent in parents[node]:
                    if cardinalities[parent] > 1:
                        exponent *= cardinalities[parent]
                canonical_partition *= math.pow(base, exponent)
        print(f"For the c-component #{i + 1} the equivalent canonical partition = {int(canonical_partition)}")    

def generateRelaxed():    
    relaxedGraph: str = ""
    unob:str = ""
    
    for index, component in enumerate(dag_components):
        currUnobLabel : str = "U" + str(index)
        unob += f", {currUnobLabel}"        
        for node in component.nodes:
            if cardinalities[node] > 1:             
                relaxedGraph += f", {currUnobLabel} -> {index_to_label[node]}"                                

    # adicionar arestas que saem do node depois - pois pode nao estar em nenhum c-component.
    for index, label in index_to_label.items():
        if cardinalities[index] > 1:
            for node in adj[index]:                
                relaxedGraph += f", {label} -> {index_to_label[node]}"

    return relaxedGraph[2:], unob[2:]

def main():
    num_nodes = int(input())
    num_edges = int(input())
    
    global adj, cardinalities, visited, parents
    adj = [[] for _ in range(num_nodes + 1)]
    cardinalities = [0] * (num_nodes + 1)
    visited = [False] * (num_nodes + 1)
    parents = [[] for _ in range(num_nodes + 1)]

    for i in range(1, num_nodes + 1):
        label, cardinality = input().split()
        cardinality = int(cardinality)
        label_to_index[label] = i
        index_to_label[i] = label
        cardinalities[i] = cardinality

    for _ in range(num_edges):
        u, v = input().split()
        u_index = label_to_index[u]
        v_index = label_to_index[v]
        adj[u_index].append(v_index)
        parents[v_index].append(u_index)

    debug(num_nodes)

    for i in range(1, num_nodes + 1):
        if not visited[i] and cardinalities[i] < 1:
            curr_nodes.clear()
            dfs(i)
            dag_components.append(CComponent(curr_nodes[:]))
            global curr_component
            curr_component += 1

    for i, component in enumerate(dag_components):
        print(f"c-component #{i + 1}")
        for node in component.nodes:
            status = "Latent" if cardinalities[node] < 1 else "Observable"
            print(f"node {node}({index_to_label[node]}) - {status}")
    


    bound_for_canonical_partitions()

    adj2, unob2 = generateRelaxed()
    print(adj2)
    print(unob2)

if __name__ == "__main__":
    main()
