#!/usr/bin/python3
import math

adj = []  # 1-indexed
parents = []  # parents of each node (dual of adj)
label_to_index = {}  # Also 1-indexed
index_to_label = {}  # debugging
cardinalities = []  # <= 1 implies unknown/unobserved
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
'''
c-component nodes: Z, X, Y
FIRST OBSERVING Z:
X:3 -> Z:2
K:2 -> Z:2
D:4 -> Z:2

EXPOENT = 3*2*4 = 24
BASE = 2

PARTIAL_CANONICA_PARTITION_1 = 2**24
------------
OBSERVING X:

W:2 -> X:3

EXPOENT = 2
BASE = 3

PARTIAL_CANONICA_PARTITION_2 = 3**2
------------
OBSERVING Z:

Z:2 -> Y:2

EXPOENT = 2
BASE = 2

PARTIAL_CANONICA_PARTITION_3 = 2**2
------------------------
TOTAL_CANONICAL_PARTITION = PARTIAL_CANONICA_PARTITION_1 * PARTIAL_CANONICA_PARTITION_2 * PARTIAL_CANONICA_PARTITION_3
TOTAL_CANONICAL_PARTITION = 2**26 * 3**2
'''
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

def main():
    print("What is the number of nodes?")
    num_nodes = int(input())
    print("What is the number of edges?")
    num_edges = int(input())
    
    global adj, cardinalities, visited, parents
    adj = [[] for _ in range(num_nodes + 1)]
    cardinalities = [0] * (num_nodes + 1)
    visited = [False] * (num_nodes + 1)
    parents = [[] for _ in range(num_nodes + 1)]

    for i in range(1, num_nodes + 1):
        print(f"Give the label and the cardinality for the {i}th node:")
        label, cardinality = input().split()
        cardinality = int(cardinality)
        label_to_index[label] = i
        index_to_label[i] = label
        cardinalities[i] = cardinality

    for i in range(num_edges):
        print(f"Give the nodes of the {i+1}th edge:")
        u, v = input().split()
        u_index = label_to_index[u]
        v_index = label_to_index[v]
        adj[u_index].append(v_index)
        parents[v_index].append(u_index)

    debug(num_nodes)

    # c-separating
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

if __name__ == "__main__":
    main()
