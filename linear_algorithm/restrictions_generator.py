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
        """
        intervention: int = self.intervention; current_targets: list[int] = [self.target]
        interventionLatent: int = self.graph.graphNodes[intervention].latentParent

        empiricalProbabilitiesVariables = [] # If V in this array then it implies P(v) in the objective function
        mechanismVariables = []              # If V in this array then it implies a decision function: 1(Pa(v) => v= some value)
        conditionalProbabilities = []        # If V|A,B,C in this array then it implies P(V|A,B,C) in the objective function
        
        while len(current_targets) > 0:
            # TODO: any node which is not a descendant of the intervention should be processed at the end.
            # TODO: check using a DFS for some variable which is in Yt and has no descendants in it.

            current_target = current_targets.pop()                       
            print(f"Current target: {current_target}")

            if not self.graph.is_descendant(ancestor=self.intervention, descendant=current_target):
                    print(f"------- Case 1: Not a descendant") # OK!
                    empiricalProbabilitiesVariables.append(current_target)
            elif self.graph.graphNodes[current_target].latentParent == interventionLatent:
                    print(f"------- Case 2: Mechanisms") # OK!
                    mechanismVariables.append(current_target)
                    for parent in self.graph.graphNodes[current_target].parents:
                        if (parent not in current_targets) and parent != intervention:
                            current_targets.append(parent)
            else:
                    print(f"------- Case 3: Find d-sepator set")
                    ancestors = self.graph.find_ancestors(node=current_target)
                    conditionableAncestors = []
                    for ancestor in ancestors:
                        if self.graph.cardinalities[ancestor] > 0 and ancestor != intervention:
                            conditionableAncestors.append(ancestor)

                    for x in range(pow(2,len(conditionableAncestors))):
                        # Consider the bits from LS to MS of x. The n-th element in conditionableAncestors is conditioned on if and only
                        # if the n-th bit from LS to MS is 1.

                        self.graph.build_moral(consideredNodes=ancestors)
                        # Remove the edges that involve any node in conditionableAncestors which is being conditioned on
                        for i in range(len(conditionableAncestors)):
                            if (x >> i) % 2 == 1:
                                conditioningNode = conditionableAncestors[i]
                                self.graph.moralGraphNodes[conditioningNode].adjacent.clear()

                                print(f"Conditioning on: {conditioningNode}")
                                for index in range(self.graph.numberOfNodes):
                                    if conditioningNode in self.graph.moralGraphNodes[index].adjacent:
                                        self.graph.moralGraphNodes[index].adjacent.remove(conditioningNode)

                            condition1 = self.graph.independency_moral(node2=interventionLatent, node1=current_target)

                            # Remove intervention outgoing edges for condition 2
                            self.graph.build_moral(consideredNodes=ancestors, flag=True, intervention=intervention)
                            condition2 = self.graph.independency_moral(node2=intervention, node1=current_target)

                            if condition1 and condition2:
                                separator: list[int] = []
                                print(f"The following set works:")
                                for element in conditionableAncestors:
                                    print(f"- {element}")
                                    separator.append(element)

                        # Choose one of the valid subsets - Last instance of "separator", for now.
                        # TODO: Determine the new y_t+1
                        # Question: is any already solved variable selected for the second time? Does the program need to address this issue
                        # by forcing the set to not contain any of such variables?

        
        # TODO: implement the objective function generator.
        print("Test completed")

    def test():
        """
        used for the development of the class. Uses the itau graph itau.txt.
        """
        graph: Graph = Graph.parse()        
        print("debug graph parsed by terminal:")
        i = 0
        for graphNode in graph.graphNodes:
            print(f"node name: {graph.indexToLabel[i]}")
            print(f"children: {graphNode.children}")
            print(f"latentParent: {graphNode.latentParent}")
            print(f"parents: {graphNode.parents}")
            i += 1
        print("\n\n\n\n")

        rg = restrictions_generator(graph=graph, intervention=graph.labelToIndex["X"], target=graph.labelToIndex["Y"])
        rg.generate_restrictions()

if __name__ == "__main__":
    restrictions_generator.test()
