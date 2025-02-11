from utils.graph import Graph

class restrictions_generator:
    """
    Given an intervention and a graph, this class finds a set of restrictions that can be used to build
    a linear objective function.
    """
    
    def __init__(self, graph: Graph, intervention: int | str, target: int | str):
        """        
        graph: an instance of the personalized class graph
        intervention: X in P(Y|do(X))
        target: Y in P(Y|do(X))
        """
        self.graph = graph
        self.intervention = intervention
        self.target = target
    
    def generate_restrictions(self):
        """
        Runs each step of the algorithm. Finds a set of variables/restrictions that linearizes the problem.

        Note: in the algorithm, variables that are classified in case 1 are all processed at the end. However, as they do not
        impact any other restriction, we might as well apply those constraints in place.
        """
        target = self.graph.secure_node_access(self.target); intervention = self.graph.secure_node_access(self.intervention)
        
        current_targets: list[int] = [target]
        empiricalProbabilitiesVariables = []
        mechanismVariables = []
        conditionalProbabilities = [] # Come from case 3: we need the probability AND

        while len(current_targets) > 0:
            current_target = current_targets.pop()
            if self.graph.is_descendant(ancester=self.intervention, descendant=current_target):
                if self.graph.graphNodes[current_target].latentParent == self.graph.graphNodes[intervention].latentParent:
                    mechanismVariables.append(current_target)
                    for parent in self.graph.graphNodes[current_target].parents:
                        current_targets.append(parent)
                else:                    
                    ancesters = [] # Find ancesters of the current_target
                    self.graph.buildMoral(ancesters) # Do we need to exclude some variables from the moral graph?
                    pass
            else:
                empiricalProbabilitiesVariables.append(current_target) 

        # TODO: implement the recursive algorithm that finds each restriction. First, define if it is case 1, 2 or 3.
        # Create a handler function for each case. Do we need to consider priorities for some case?

        print("Test completed")

    def test():
        """
        used for the development of the class. Uses the itau graph itau.txt.
        """
        graph: Graph = Graph.parse()        
        print("debug graph parsed by terminal:")
        for graphNode in graph.graphNodes:
            print(f"children: {graphNode.children}")
            print(f"latentParent: {graphNode.latentParent}")
            print(f"parents: {graphNode.parents}")

        rg = restrictions_generator(graph=graph, intervention="X", target="Y")
        rg.generate_restrictions()

if __name__ == "__main__":
    restrictions_generator.test()
