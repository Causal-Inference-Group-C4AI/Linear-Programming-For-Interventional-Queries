from scipy.optimize import linprog
import os
import argparse

import pandas as pd

from causal_usp_icti.graph.graph import Graph, get_graph
from causal_usp_icti.linear_algorithm.linear_constraints import generate_constraints
from causal_usp_icti.linear_algorithm.obj_function_generator import ObjFunctionGenerator
from causal_usp_icti.utils._enum import DirectoriesPath


class OptProblemBuilder:
    def __init__(self):
        pass

    def get_query(self, str_graph: str, unobservables: list[str], intervention: str, intervention_value: int, target: str, target_value: int, csv_path):
        graph = get_graph(str_graph=str_graph, unobservables=unobservables)
        self.builder_linear_problem(graph, csv_path, intervention, intervention_value, target, target_value)

        
    def builder_linear_problem(self, graph: Graph, csv_path, intervention: str, intervention_value: int, target: str, target_value: int):
    # def builder_linear_problem(input_path, csv_path):
        # graph: Graph = get_graph(input_path)
        df = pd.read_csv(csv_path)

        # interventionVariable = input(
        #     "Provide the label of the intervention:").strip()
        # interventionVariable = (
        #     interventionVariable if len(interventionVariable) else "X"
        # )
        interventionVariable = intervention


        # interventionValue = input(
        #     "Provide the value of the intervention:").strip()
        # interventionValue = int(interventionValue) if len(
        #     interventionValue) else 0
        interventionValue = intervention_value

        # targetVariable = input("Provide the label of the target:").strip()
        # targetVariable = targetVariable if len(targetVariable) else "Y"
        targetVariable = target

        # targetValue = input("Provide the value of the target:").strip()
        # targetValue = int(targetValue) if len(targetValue) else 1
        targetValue = target_value

        objFG = ObjFunctionGenerator(
            graph=graph,
            dataFrame=df,
            intervention=graph.labelToIndex[interventionVariable],
            interventionValue=interventionValue,
            target=graph.labelToIndex[targetVariable],
            targetValue=targetValue,
            empiricalProbabilitiesVariables=[],
            mechanismVariables=[],
            conditionalProbabilitiesVariables={},
            debugOrder=[],
        )
        objFG.find_linear_good_set()
        mechanisms = objFG.get_mechanisms_pruned()
        objFunctionCoefficients = objFG.build_objective_function(mechanisms)

        interventionLatentParent = objFG.graph.graphNodes[
            objFG.intervention
        ].latentParent
        cComponentEndogenous = objFG.graph.graphNodes[interventionLatentParent].children
        consideredEndogenousNodes = list(
            (set(cComponentEndogenous) & set(
                objFG.debugOrder)) | {
                objFG.intervention})

        probs, decisionMatrix = generate_constraints(
            data=df,
            dag=objFG.graph,
            unob=objFG.graph.graphNodes[objFG.intervention].latentParent,
            consideredCcomp=consideredEndogenousNodes,
            mechanism=mechanisms,
        )

        print("-- DEBUG OBJ FUNCTION --")
        for i, coeff in enumerate(objFunctionCoefficients):
            print(f"c_{i} = {coeff}")

        print("-- DECISION MATRIX --")
        for i in range(len(decisionMatrix)):
            for j in range(len(decisionMatrix[i])):
                print(f"{decisionMatrix[i][j]} ", end="")
            print(f" = {probs[i]}")
        intervals = [(0, 1) for _ in range(len(decisionMatrix[0]))]
        lowerBoundSol = linprog(
            c=objFunctionCoefficients,
            A_ub=None,
            b_ub=None,
            A_eq=decisionMatrix,
            b_eq=probs,
            method="highs",
            bounds=intervals,
        )
        lowerBound = lowerBoundSol.fun

        upperBoundSol = linprog(
            c=[-x for x in objFunctionCoefficients],
            A_ub=None,
            b_ub=None,
            A_eq=decisionMatrix,
            b_eq=probs,
            method="highs",
            bounds=intervals,
        )

        upperBound = -upperBoundSol.fun

        print(
            f"Causal query: P({targetVariable}={targetValue}|do({interventionVariable}={interventionValue}))"
        )
        print(f"Bounds: {lowerBound} <= P <= {upperBound}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets causal inference under Partial-Observability."
    )
    parser.add_argument(
        "input_filename",
        help="The name of the input file in test_case/input directory")
    parser.add_argument("csv_filename", help="The name of the csv")
    args = parser.parse_args()

    input_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),
        f"../../{DirectoriesPath.TEST_CASES_INPUTS.value}/{args.input_filename}.txt",
    )
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"../../{DirectoriesPath.CSV_PATH.value}/{args.csv_filename}.csv",
    )
    OptProblemBuilder.builder_linear_problem(input_path, csv_path)
    # graph: Graph = Graph.parse()
    # _,_,mechanism = MechanismGenerator.mechanisms_generator(latentNode = graph.labelToIndex["U1"], endogenousNodes = [graph.labelToIndex["Y"], graph.labelToIndex["X"]], cardinalities=graph.cardinalities ,
    # graphNodes = graph.graphNodes, v= False )

    # df: pd.DataFrame = pd.read_csv("/home/joaog/Cpart/Canonical-Partition/causal_usp_icti/linear_algorithm/balke_pearl.csv")
    # probs, decisionMatrix = generateConstraints(data=df ,dag= graph, unob=graph.labelToIndex["U1"],consideredCcomp=[graph.labelToIndex["X"], graph.labelToIndex["Y"]],mechanism=mechanism)
    # objFun = []
    # for u in range(len(mechanism)):
    #     coef = 0
    #     if mechanism[u]["2=0"] == 1:
    #         coef = 1
    #     objFun.append(coef)
    # intervals = [(0, 1) for _ in range(len(mechanism))]

    # lowerBoundSol = linprog(c=objFun, A_ub=None, b_ub=None,
    #                             A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)
    # lowerBound = lowerBoundSol.fun

    # upperBoundSol = linprog(c=[-x for x in objFun], A_ub=None, b_ub=None,
    #                             A_eq=decisionMatrix, b_eq=probs, method="highs", bounds=intervals)
    # upperBound = -upperBoundSol.fun

    # print("-- DEBUG OBJ FUNCTION --")
    # for i, coeff in enumerate(objFun):
    #     print(f"c_{i} = {coeff}")

    # print(f"Bounds: {lowerBound} <= P <= {upperBound}")
