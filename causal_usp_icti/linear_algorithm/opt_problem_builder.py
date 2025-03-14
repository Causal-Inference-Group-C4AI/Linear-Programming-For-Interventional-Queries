from causal_usp_icti.linear_algorithm.linearConstraints import generateConstraints
from causal_usp_icti.linear_algorithm.obj_function_generator import ObjFunctionGenerator
from causal_usp_icti.graph.graph import Graph
from causal_usp_icti.utils.mechanisms_generator import MechanismGenerator
from scipy.optimize import linprog
import pandas as pd
class OptProblemBuilder:
    def builder_linear_problem():
        graph: Graph = Graph.parse()        
        
        csvPath: str = input("Provide the path for the .csv file:").strip()
        csvPath = csvPath if len(csvPath) else "itau.csv"
        df = MechanismGenerator.fetchCsv(filepath=csvPath)
        
        interventionVariable = input("Provide the label of the intervention:").strip()
        interventionVariable = interventionVariable if len(interventionVariable) else "X"
        
        interventionValue = input("Provide the value of the intervention:").strip()
        interventionValue = int(interventionValue) if len(interventionValue) else 0
        
        targetVariable = input("Provide the label of the target:").strip()
        targetVariable = targetVariable if len(targetVariable) else "Y"
        
        targetValue = input("Provide the value of the target:").strip()
        targetValue = int(targetValue) if len(targetValue) else 1

        objFG = ObjFunctionGenerator(graph=graph, dataFrame=df,
                                    intervention=graph.labelToIndex[interventionVariable], interventionValue=interventionValue, 
                                    target=graph.labelToIndex[targetVariable], targetValue=targetValue,
                                    empiricalProbabilitiesVariables=[], mechanismVariables=[], 
                                    conditionalProbabilitiesVariables={}, debugOrder=[])
        objFG.find_linear_good_set()
        mechanisms = objFG.get_mechanisms_pruned()
        objFunctionCoefficients = objFG.build_objective_function(mechanisms)

        probs, decisionMatrix = generateConstraints(data=df, dag=objFG.graph, 
                                                    unob=objFG.graph.graphNodes[objFG.intervention].latentParent,consideredCcomp=[graph.labelToIndex["Y"], graph.labelToIndex["X"]],
                                                    mechanism=mechanisms)
        
        intervals = [(0, 1) for _ in range(len(mechanisms))]
        
        lowerBoundSol = linprog(c=objFunctionCoefficients, A_ub=None, b_ub=None, 
                                A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)        
        lowerBound = lowerBoundSol.fun
        
        upperBoundSol = linprog(c=[-x for x in objFunctionCoefficients], A_ub=None, b_ub=None, 
                                A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)
        upperBound = -upperBoundSol.fun

        print("-- DEBUG OBJ FUNCTION --")
        for i, coeff in enumerate(objFunctionCoefficients):
            print(f"c_{i} = {coeff}")
    
        print(f"Causal query: P({targetVariable}={targetValue}|do({interventionVariable}={interventionValue}))")
        print(f"Bounds: {lowerBound} <= P <= {upperBound}")

if __name__ == "__main__":
    #OptProblemBuilder.builder_linear_problem()
    graph: Graph = Graph.parse()
    _,_,mechanism = MechanismGenerator.mechanisms_generator(latentNode =graph.labelToIndex["U1"], endogenousNodes = [graph.labelToIndex["Y"], graph.labelToIndex["X"]], cardinalities=graph.cardinalities , 
                                                        graphNodes = graph.graphNodes, v= False )

    df: pd.DataFrame = pd.read_csv("/home/joaog/Cpart/Canonical-Partition/causal_usp_icti/linear_algorithm/balke_pearl.csv")
    probs, decisionMatrix = generateConstraints(data=df ,dag= graph, unob=graph.labelToIndex["U1"],consideredCcomp=[graph.labelToIndex["X"], graph.labelToIndex["Y"]],mechanism=mechanism)
    objFun = []
    for u in range(len(mechanism)):
        coef = 0
        if mechanism[u]["2=1"] == 1:
            coef = 1
        objFun.append(coef)
    intervals = [(0, 1) for _ in range(len(mechanism))]
        
    lowerBoundSol = linprog(c=objFun, A_ub=None, b_ub=None, 
                                A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)        
    lowerBound = lowerBoundSol.fun
        
    upperBoundSol = linprog(c=[-x for x in objFun], A_ub=None, b_ub=None, 
                                A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)
    upperBound = -upperBoundSol.fun

    print("-- DEBUG OBJ FUNCTION --")
    for i, coeff in enumerate(objFun):
        print(f"c_{i} = {coeff}")
    
    print(f"Bounds: {lowerBound} <= P <= {upperBound}")