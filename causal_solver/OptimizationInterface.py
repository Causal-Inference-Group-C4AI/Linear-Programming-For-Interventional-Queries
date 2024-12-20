from causal_solver.NonLinearConstraints import NonLinearConstraints
from causal_solver.NonLinearSolver import solveModel
from partition_methods.relaxed_problem.python.graph import Graph 
from causal_solver.Helper import Helper
from causal_solver.SupertailFinder import SupertailFinder
from causal_solver.Supersets import Supersets

from collections import namedtuple

equationsObject = namedtuple('equationsObject', ['probability', 'dictionary'])
latentAndCcomp = namedtuple('latentAndCcomp', ['latent', 'nodes'])

class OptimizationInterface:
    def optimizationProblem(fromInterface=False, nodesStr="", edgesStr="", verbose=False):
        print(f"Please, enter the graph in the default format")
        dag: Graph = Graph.parse(fromInterface=fromInterface,nodesString=nodesStr, edgesString=edgesStr)
        print("Please, enter a path for the csv")
        csvPath: str = input()

        print(f"For an inference P(Y=y|do(X=x)) please, enter, in this order: X, x, Y, y")
        interventionVariableLabel, interventionVariableValue, targetVariableLabel, targetVariableValue = input().split()
        interventionVariable      = dag.labelToIndex[interventionVariableLabel]
        targetVariable            = dag.labelToIndex[targetVariableLabel]
        interventionVariableValue = int(interventionVariableValue)
        targetVariableValue       = int(targetVariableValue)

        setS, setT, setU = SupertailFinder.findSuperTail(interventionNode=interventionVariable, targetNode=targetVariable, graphNodes=dag.graphNodes)
        listS, listT, listU = (list(setS), list(setT), list(setU))

        mechanismDictsList, latentCardinalities = Helper.mechanismListGenerator(cardinalities=dag.cardinalities,
                                listU=listU, setS=(setS|set([interventionVariable])), graphNodes=dag.graphNodes)        

        objectiveFunction: dict[str, int] = NonLinearConstraints.objectiveFunctionBuilder(mechanismDictsList=mechanismDictsList,
                                    graphNodes=dag.graphNodes,
                                    cardinalities=dag.cardinalities,
                                    listS=listS, listT=listT, listU=listU,
                                    interventionVariable=interventionVariable,
                                    interventionValue=interventionVariableValue,
                                    targetVariable=targetVariable,
                                    targetValue=targetVariableValue,
                                    topoOrder=dag.topologicalOrder,
                                    filepath=csvPath,
                                    indexToLabel=dag.indexToLabel,
                                    verbose=verbose
                                    )

        completeSetS = setS | set([interventionVariable])
        triples: list[Supersets] = []
        latentSetsDict: dict[int, Supersets] = {}
        for latentCompanion in listU:
            auxS, auxT, auxU = SupertailFinder.findSuperTailLatent(latentCompanion, dag.graphNodes, completeSetS)
            triples.append(Supersets(listS=auxS, listU=auxU, listT=auxT))
            latentSetsDict[latentCompanion] = Supersets(listS=auxS, listU=[latentCompanion], listT=auxT)
        
        simplifiedTriples: list[Supersets] = Helper.equationsSimplifier(triples=triples, 
                                            latentSetsDict=latentSetsDict,latentList=listU) 

        tripleEquations: list[list[equationsObject]] = []
        for triple in simplifiedTriples:
            equations: list[equationsObject] = NonLinearConstraints.equationsGenerator(mechanismDictsList=mechanismDictsList,
                                    listT=triple.listT,
                                    listS=triple.listS,
                                    listU=triple.listU,
                                    cardinalities=dag.cardinalities,
                                    graphNodes=dag.graphNodes,
                                    topoOrder=dag.topologicalOrder,
                                    indexToLabel=dag.indexToLabel,
                                    filepath=csvPath
                                    )
            tripleEquations.append(equations)

        return solveModel(objective=objectiveFunction, constraints=tripleEquations,latentCardinalities=latentCardinalities,verbose=False,initVal=.5)

def testBuildProblem():
    obj, equations, _ = OptimizationInterface.optimizationProblem(verbose=True)

    dbgCnt = 100
    for i, eq in enumerate(equations[0]):
            if i == dbgCnt:
                break

            print(f"Equation {i + 1}:\nprob = {eq.probability}\n")
            for j, key in enumerate(eq.dictionary):
                if j == dbgCnt:
                    break
                print(f"for key = {key}, coefficient = {eq.dictionary[key]}")

def testSolution():
    lower, upper = OptimizationInterface.optimizationProblem(verbose = False)
    print(f"Results: [{lower},{upper}]")

if __name__ == "__main__":
    # testBuildProblem()
    testSolution()