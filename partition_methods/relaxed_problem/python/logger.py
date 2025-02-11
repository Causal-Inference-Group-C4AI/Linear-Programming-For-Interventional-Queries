from utils.graph import Graph
class Logger:        
    def debugGraph(graph: Graph):        
        print("debug indexToLabel", graph.cardinalities)        
        for index, label in graph.indexToLabel.items():
            print(f"index {index} label {label}")

        print("debug labelToIndex", graph.cardinalities)
        for label, index in graph.labelToIndex.items():
            print(f"label {label} index {index}")

        print("Latent variables: \n")
        for i in range(1, graph.numberOfNodes + 1):
            if graph.cardinalities[i] < 1:
                print(f"latent var {i} with label {graph.indexToLabel[i]}")

        print("debugging graph:\n", graph.cardinalities)
        for i in range(1, graph.numberOfNodes + 1):
            print(f"Edges from {graph.indexToLabel[i]}")
            for el in graph.adj[i]:
                print(graph.indexToLabel[el] + " ")        

    def debugCcomponents(graph: Graph):        
        for i, component in enumerate(graph.dagComponents):
            print(f"c-component #{i + 1}")
            for node in component.nodes:
                status = "Latent" if graph.cardinalities[node] < 1 else "Observable"
                print(f"node {node}({graph.indexToLabel[node]}) - {status}")