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
        conditionalProbabilities: list[tuple[int, list[int]]] = []        # If V|A,B,C in this array then it implies P(V|A,B,C) in the objective function
        
        while len(current_targets) > 0:
            print("---- Current targets array:")
            for tg in current_targets:
                print(f"- {tg}")
            
            # TODO: check if the topological order is reversed.
            current_target = -1
            for node in self.graph.topologicalOrder:
                if node in current_targets and node > current_target:
                    current_target = node                            
            
            current_targets.remove(current_target)                       
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
                    print(f"------- Case 3: Find d-separator set")
                    ancestors = self.graph.find_ancestors(node=current_target)
                    conditionableAncestors: list[int] = []
                    for ancestor in ancestors:
                        # Question: does it need to not be the intervention?
                        if self.graph.cardinalities[ancestor] > 0 and ancestor != current_target: 
                            conditionableAncestors.append(ancestor)

                    alwaysConditionedNodes: list[int] = current_targets.copy()
                    if current_target in alwaysConditionedNodes: alwaysConditionedNodes.remove(current_target)                    
                    
                    if interventionLatent in alwaysConditionedNodes: alwaysConditionedNodes.remove(interventionLatent)

                    for x in range(pow(2,len(conditionableAncestors))):                                                                        
                        conditionedNodes: list[int] = alwaysConditionedNodes.copy()
                        for i in range(len(conditionableAncestors)):
                            if (x >> i) % 2 == 1:
                                conditionedNodes.append(conditionableAncestors[i])
                      
                        self.graph.build_moral(consideredNodes=ancestors,conditionedNodes=conditionedNodes)                                             
                        condition1 = self.graph.independency_moral(node2=interventionLatent, node1=current_target)
                        
                        self.graph.build_moral(consideredNodes=ancestors, conditionedNodes=conditionedNodes, flag=True, intervention=intervention)
                        condition2 = self.graph.independency_moral(node2=intervention, node1=current_target)

                        if condition1 and condition2:
                            separator: list[int] = []
                            print(f"The following set works:")
                            for element in conditionedNodes:
                                print(f"- {element}")
                                separator.append(element)

                            current_targets = list((set(current_targets) | set(conditionedNodes)) - {intervention, current_target})
                        
                        # Choose one of the valid subsets - Last instance of "separator", for now
                        conditionalProbabilities.append((current_target, conditionedNodes))
                        
                        
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
        
        for i in range(graph.numberOfNodes):
            print(f"node index {i} - node name: {graph.indexToLabel[i]}")
            print(f"children: {graph.graphNodes[i].children}")
            print(f"latentParent: {graph.graphNodes[i].latentParent}")
            print(f"parents: {graph.graphNodes[i].parents}")            
        print("\n\n\n\n")

        rg = restrictions_generator(graph=graph, intervention=graph.labelToIndex["X"], target=graph.labelToIndex["Y"])
        rg.generate_restrictions()

if __name__ == "__main__":
    restrictions_generator.test()
