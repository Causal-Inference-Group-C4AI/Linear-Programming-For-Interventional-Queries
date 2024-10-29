from test_cases.generator.dataGen import dataGen
from partition_methods.relaxed_problem.python.graph import Graph

def main():
    graph = Graph.parse("/home/lawand/Canonical-Partition/test_cases/inputs/test-itau-simples.txt")
    data = dataGen(graph)



if __name__ == "__main__":
    main()
