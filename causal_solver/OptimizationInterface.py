from causal_solver.NonLinearConstraints import NonLinearConstraints
from partition_methods.relaxed_problem.python.graph import Graph 
from causal_solver.Helper import Helper
from causal_solver.SupertailFinder import Node, SupertailFinder
from collections import namedtuple

equationsObject = namedtuple('equationsObject', ['probability', 'dictionary'])
latentAndCcomp = namedtuple('latentAndCcomp', ['latent', 'nodes'])

class OptimizationInterface:
    def optimizationProblem(verbose: bool):
        print(f"Please, enter the graph in the default format")
        dag: Graph = Graph.parse()
        
        print(f"For an inference P(Y=y|do(X=x)) please, enter, in this order: X, x, Y, y")
        interventionVariableLabel, interventionVariableValue, targetVariableLabel, targetVariableValue = input().split()
        interventionVariable = dag.labelToIndex[interventionVariableLabel]
        targetVariable       = dag.labelToIndex[targetVariableLabel]
        interventionVariableValue = int(interventionVariableValue)
        targetVariableValue = int(targetVariableValue)

        setS, setT, setU = SupertailFinder.findSuperTail(node1=interventionVariable, node2=targetVariable, graphNodes=dag.graphNodes)
        print(f"Debug supertail algorithm:\nlistS: {setS}\nlistU: {setU}\nlistT: {setT}")

        mechanismDictsList, _ = Helper.mechanismListGenerator(cardinalities=dag.cardinalities,
                                setU=list(setU), graphNodes=dag.graphNodes)

        objectiveFunction: dict[str, int] = NonLinearConstraints.objectiveFunctionBuilder(mechanismDictsList=mechanismDictsList,
                                    graphNodes=dag.graphNodes,
                                    cardinalities=dag.cardinalities,
                                    listS=list(setS), listT=list(setT), listU=list(setU),
                                    interventionVariable=interventionVariable,
                                    interventionValue=interventionVariableValue,
                                    targetVariable=targetVariable,
                                    targetValue=targetVariableValue,
                                    topoOrder=dag.topologicalOrder,
                                    filepath="itau.csv",
                                    indexToLabel=dag.indexToLabel,
                                    verbose=verbose
                                    )

        equations: list[equationsObject] = NonLinearConstraints.equationsGenerator(mechanismDictsList=mechanismDictsList,
                                    setT=list(setT),
                                    setS=list(setS),
                                    setU=list(setU),
                                    cardinalities=dag.cardinalities,
                                    graphNodes=dag.graphNodes,
                                    topoOrder=dag.topologicalOrder,
                                    indexToLabel=dag.indexToLabel,
                                    filepath='itau.csv'
                                    )      
        return objectiveFunction, equations
        
def main():
    obj, equations = OptimizationInterface.optimizationProblem(verbose=True)    

    dbgCnt = 3
    for i, eq in enumerate(equations):
        if i == dbgCnt:
            break        

        print(f"Equation {i + 1}:\nprob = {eq.probability}\n")
        for j, key in enumerate(eq.dictionary):
            if j == dbgCnt:
                break            
            print(f"for key = {key}, coefficient = {eq.dictionary[key]}")

if __name__ == "__main__":
    main()
        