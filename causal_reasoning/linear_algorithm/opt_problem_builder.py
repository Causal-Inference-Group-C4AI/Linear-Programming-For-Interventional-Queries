from scipy.optimize import linprog
import gurobipy as gp
import pandas as pd

from causal_reasoning.graph.graph import Graph
from causal_reasoning.linear_algorithm.linear_constraints import generate_constraints
from causal_reasoning.linear_algorithm.obj_function_generator import ObjFunctionGenerator

class MasterProblem:
    def __init__(self):
        self.model = gp.Model("linear")
        self.vars = None
        self.constrs = None
        
    def setup(self, probs, decisionMatrix, objFunctionCoefficients: list[float], modelSense: int = 1):
        num_vars = len(decisionMatrix[0])
        self.vars = self.model.addVars(num_vars, obj=1, name="Variables")
        
        self.constrs = self.model.addConstrs(
            (gp.quicksum(decisionMatrix[i][j] * self.vars[j] for j in range(num_vars)) == probs[i]
            for i in range(len(probs))),
            name="Constraints"
        )

        if modelSense == 1:
            self.model.modelSense = gp.GRB.MINIMIZE
        else:
            self.model.modelSense = gp.GRB.MAXIMIZE
        self.model.setObjective(gp.quicksum(objFunctionCoefficients[i] * self.vars[i] for i in range(len(objFunctionCoefficients))))
        
        # Turning off output because of the iterative procedure
        self.model.params.outputFlag = 0
        self.model.update()
        
    # def update(self, pattern, index):
    #     new_col = gp.Column(coeffs=pattern, constrs=self.constrs.values())
    #     self.vars[index] = self.model.addVar(obj=1, column=new_col,
    #                                          name=f"Pattern[{index}]")
    #     self.model.update()


class OptProblemBuilder:
    def builder_linear_problem(
        graph: Graph,
        df: pd.DataFrame,
        intervention: str,
        intervention_value: int,
        target: str,
        target_value: int,
    ):
        objFG = ObjFunctionGenerator(
            graph=graph,
            dataFrame=df,
            intervention=graph.labelToIndex[intervention],
            intervention_value=intervention_value,
            target=graph.labelToIndex[target],
            target_value=target_value,
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
            (set(cComponentEndogenous) & set(objFG.debugOrder)) | {objFG.intervention}
        )

        probs, decisionMatrix = generate_constraints(
            data=df,
            dag=objFG.graph,
            unob=objFG.graph.graphNodes[objFG.intervention].latentParent,
            consideredCcomp=consideredEndogenousNodes,
            mechanism=mechanisms,
        )

        #print("-- DEBUG OBJ FUNCTION --")
        # for i, coeff in enumerate(objFunctionCoefficients):
            #print(f"c_{i} = {coeff}")

        #print("-- DECISION MATRIX --")
        # for i in range(len(decisionMatrix)):
            # for j in range(len(decisionMatrix[i])):
                #print(f"{decisionMatrix[i][j]} ", end="")
            #print(f" = {probs[i]}")
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
            f"Causal query: P({target}={target_value}|do({intervention}={intervention_value}))"
        )
        print(f"Bounds: {lowerBound} <= P <= {upperBound}")

    def gurobi_builder_problem(graph: Graph,
        df: pd.DataFrame,
        intervention: str,
        intervention_value: int,
        target: str,
        target_value: int,
    ):
        objFG = ObjFunctionGenerator(
            graph=graph,
            dataFrame=df,
            intervention=graph.labelToIndex[intervention],
            intervention_value=intervention_value,
            target=graph.labelToIndex[target],
            target_value=target_value,
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
            (set(cComponentEndogenous) & set(objFG.debugOrder)) | {objFG.intervention}
        )

        probs, decisionMatrix = generate_constraints(
            data=df,
            dag=objFG.graph,
            unob=objFG.graph.graphNodes[objFG.intervention].latentParent,
            consideredCcomp=consideredEndogenousNodes,
            mechanism=mechanisms,
        )

        #print("-- DEBUG OBJ FUNCTION --")
        # for i, coeff in enumerate(objFunctionCoefficients):
        #     #print(f"c_{i} = {coeff}")

        # #print("-- DECISION MATRIX --")
        # for i in range(len(decisionMatrix)):
        #     for j in range(len(decisionMatrix[i])):
                #print(f"{decisionMatrix[i][j]} ", end="")
            #print(f" = {probs[i]}")

        master = MasterProblem()
        modelSenseMin = 1
        master.setup(probs, decisionMatrix, objFunctionCoefficients, modelSenseMin)
        master.model.optimize()

        # duals = master.model.getAttr("pi", master.constrs)
        # #print(f"duals: {duals}")
        if master.model.Status == gp.GRB.OPTIMAL: # OPTIMAL
                lower = master.model.objVal
                #print(f"Minimal solution found!\nMIN Query: {lower}")
        else:
            #print(f"Minimal solution not found. Gurobi status code: {master.model.Status}")
            lower = None
        modelSenseMax = -1
        master.setup(probs, decisionMatrix, objFunctionCoefficients, modelSenseMax)
        master.model.optimize()

        # duals = master.model.getAttr("pi", master.constrs)
        # #print(f"duals: {duals}")
        if master.model.Status == gp.GRB.OPTIMAL: # OPTIMAL
                upper = master.model.objVal
                #print(f"Maximal solution found!\nMAX Query: {upper}")
        else:
            #print(f"Maximal solution not found. Gurobi status code: {master.model.Status}")
            upper = None

        #print(
        #     f"Causal query: P({target}={target_value}|do({intervention}={intervention_value}))"
        # )
        #print(f"Bounds: {lower} <= P <= {upper}")
        return lower, upper
