import pyomo.environ  as pyo
from collections import namedtuple
from pyomo.opt import * 
import gurobipy as gp
from gurobipy import GRB
import numpy as np

equationsObject = namedtuple('equationsObject', ['probability', 'dictionary'])

def dictKey_to_index(key : str):
    unobCardinalities: list[int] = []
    commma_index: list[int] = [0]

    for index,num in enumerate(key):
        if num == ",":
            unobCardinalities.append(int(key[commma_index[-1]:index]))
            commma_index.append(index + 1)
        elif index == len(key) - 1:
            unobCardinalities.append(int(key[commma_index[-1]:]))
    return unobCardinalities


def createModel(objective : dict[str, float], constraints : list[list[equationsObject]],latentCardinalities: list[int], maximize : bool = False,
                 initVal: float = .5):
    numVar: int = 0
    latentsNums: list[int] = [0]

    for key in latentCardinalities:
        latentsNums.append(latentCardinalities[key] + numVar)
        numVar += latentCardinalities[key]

    model = pyo.ConcreteModel(name = "opt")
    model.q = pyo.Var(range(numVar), bounds=(0,1), within = pyo.Reals, initialize = initVal)
    model.eqConstrain = pyo.ConstraintList()
    def o_rule(model):
        expr = 0
        for key in objective:
            coef = objective[key]
            unobs = dictKey_to_index(key= key)

            if coef > 0:
                aux = coef
                for u in unobs:
                    aux *= model.q[u]
                expr += aux
        return expr
    if maximize :
        model.obj = pyo.Objective(rule = o_rule, sense = pyo.maximize)
    else:
        model.obj = pyo.Objective(rule = o_rule, sense = pyo.minimize)
    for group in constraints:
        for eqn in group:
            expr = 0
            for key in eqn.dictionary:
                coef = eqn.dictionary[key]
                unobs = dictKey_to_index(key = key)
                if coef > 0:
                        aux = coef
                        for u in unobs:
                            aux *= model.q[u]
                        expr += aux
            model.eqConstrain.add((expr == eqn.probability))

    for i in range(1, len(latentsNums)):
        expr = 0
        for var in range(latentsNums[i -1], latentsNums[i]):
            expr += model.q[var]
        model.eqConstrain.add(expr == 1.)
    return model



def solveModel(objective: dict[str, float], constraints: list[list[equationsObject]], latentCardinalities: dict[str, int], verbose: bool = False,
                initVal: float = .5):
    
    # Create a copy of the model for maximization
    model_max = gp.Model("bilinear_optimization")
    model_max.setParam("OutputFlag", 0 if not verbose else 1)
    model_max.setParam("FeasibilityTol", 1e-6)
    model_max.setParam("NonConvex", 2)

    # Create a copy of the model for minimization
    model_min = gp.Model("bilinear_optimization")
    model_min.setParam("OutputFlag", 0 if not verbose else 1)
    model_min.setParam("FeasibilityTol", 1e-6)
    model_min.setParam("NonConvex", 2)
    
    numVar = sum(latentCardinalities.values())
    q_max = model_max.addVars(numVar, lb=0, ub=1, vtype=GRB.INTEGER, name="q")
    q_min = model_min.addVars(numVar, lb=0, ub=1, vtype=GRB.INTEGER, name="q")

    print(f"Model max variables: {[var for var in model_max.getVars()]}")
    print(f"Model min variables: {[var for var in model_min.getVars()]}")

    # Initialize variables
    if isinstance(initVal, (list, np.ndarray)):
        for i in range(numVar):
            q_max[i].start = initVal[i]
            q_min[i].start = initVal[i]
    else:
        for i in range(numVar):
            q_max[i].start = initVal
            q_min[i].start = initVal
    
    # Build the objective expression for maximization
    expr_max = 0
    for key, coef in objective.items():
        unobs = dictKey_to_index(key)
        if coef > 0:
            aux = coef
            for u in unobs:
                aux *= q_max[u]
            expr_max += aux
    
    # Set the objective for maximization
    model_max.setObjective(expr_max, GRB.MAXIMIZE)
    


    for u in unobs:
        if u not in q_max:
            print(f"Error: Index {u} not in q_max")
        if u not in q_min:
            print(f"Error: Index {u} not in q_min")


    # Add the constraints (same for both models)
    for group in constraints:
        for eqn in group:
            expr = 0
            for key in eqn.dictionary:
                coef = eqn.dictionary[key]
                unobs = dictKey_to_index(key)
                if coef > 0:
                    aux = coef
                    for u in unobs:
                        aux *= q_max[u]
                    expr += aux
            print(f"eqn.probability: {eqn.probability}")
            model_max.addConstr(expr == eqn.probability)
            model_min.addConstr(expr == eqn.probability)
    
    # Add latent sum constraints (same for both models)
    latentsNums = [0]
    for key, cardinality in latentCardinalities.items():
        latentsNums.append(latentsNums[-1] + cardinality)
    
    for i in range(1, len(latentsNums)):
        expr = 0
        for var in range(latentsNums[i - 1], latentsNums[i]):
            expr += q_max[var]
        model_max.addConstr(expr == 1.0)
        model_min.addConstr(expr == 1.0)
    
    # Solve the maximization problem
    model_max.optimize()
    upper = model_max.objVal
    print(f"MAX Query: {upper}")

    # Build the objective expression for minimization
    expr_min = 0
    for key, coef in objective.items():
        unobs = dictKey_to_index(key)
        if coef > 0:
            aux = coef
            for u in unobs:
                aux *= q_min[u]
            expr_min += aux
    
    # Set the objective for minimization
    model_min.setObjective(expr_min, GRB.MINIMIZE)
    
    # Solve the minimization problem
    model_min.optimize()
    lower = model_min.objVal
    print(f"MIN Query: {lower}")

    return lower, upper
