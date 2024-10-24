#!/usr/bin/python3

from partition_methods.relaxed_problem.python.graph import Graph

def main():
    graph: Graph = Graph.parse()
    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    
    print(graph.adj)


#test function
if __name__ == "__main__":
    main()
