from collections import namedtuple
from pyomo.opt import * 
import gurobipy as gp
from gurobipy import GRB, Model
import numpy as np

import pandas as pd



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

def solveModelGurobi(objective: dict[str, float], constraints: list[list[equationsObject]], latentCardinalities: dict[str, int], verbose: bool = False,
                initVal: float = .5):
    return minimizeModel(objective, constraints, latentCardinalities, verbose, initVal), \
            maximizeModel(objective, constraints, latentCardinalities, verbose, initVal)


def maximizeModel(objective: dict[str, float], constraints: list[list[equationsObject]], latentCardinalities: dict[str, int], verbose: bool = False,
                initVal: float = .5):
    # Create the model for maximization
    # model_max = gp.Model("multilinear_optimization")
    model_max = gp.Model("bilinear_optimization")
    model_max.setParam("OutputFlag", 0 if not verbose else 1)
    model_max.setParam("FeasibilityTol", 1e-2)
    # model_max.setParam("NonConvex", 2)
    
    numVar = sum(latentCardinalities.values())
    q_max = model_max.addVars(numVar, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="q")

    # Initialize variables
    if isinstance(initVal, (list, np.ndarray)):
        for i in range(numVar):
            q_max[i].start = initVal[i]
    else:
        for i in range(numVar):
            q_max[i].start = initVal
    
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
    
    print(f"Model max variables: {[var for var in model_max.getVars()]}")
    
    # Add latent sum constraints (same for both models)
    latentsNums = [0]
    for key, cardinality in latentCardinalities.items():
        latentsNums.append(latentsNums[-1] + cardinality)
    
    for i in range(1, len(latentsNums)):
        expr = 0
        for var in range(latentsNums[i - 1], latentsNums[i]):
            expr += q_max[var]
        model_max.addConstr(expr == 1.0)
    
    # Solve the maximization problem
    model_max.optimize()
    if model_max.Status == GRB.OPTIMAL: # OPTIMAL
        upper = model_max.objVal
        print(f"Maximal solution found!\nMAX Query: {upper}")
    else:
        print(f"Maximal solution not found. Gurobi status code: {model_max.Status}")
        upper = 0

    return upper


def minimizeModel(objective: dict[str, float], constraints: list[list[equationsObject]], latentCardinalities: dict[str, int], verbose: bool = True,
                initVal: float = .5):
    # Create the model for minimization
    # model_min = gp.Model("multilinear_optimization")
    model_min = gp.Model("bilinear_optimization")
    model_min.setParam("OutputFlag", 0 if not verbose else 1)
    model_min.setParam("FeasibilityTol", 1e-2)
    # model_min.setParam("NonConvex", 2)
    
    numVar = sum(latentCardinalities.values())
    q_min = model_min.addVars(numVar, lb=0, ub=1, vtype=GRB.CONTINUOUS, name="q")

    # Initialize variables
    if isinstance(initVal, (list, np.ndarray)):
        for i in range(numVar):
            q_min[i].start = initVal[i]
    else:
        for i in range(numVar):
            q_min[i].start = initVal
    
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
    

    for u in unobs:
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
                        aux *= q_min[u]
                    expr += aux
            print(f"eqn.probability: {eqn.probability}")
            model_min.addConstr(expr == eqn.probability)
    
    print(f"Model min variables: {[var for var in model_min.getVars()]}")
    
    # Add latent sum constraints (same for both models)
    latentsNums = [0]
    for key, cardinality in latentCardinalities.items():
        latentsNums.append(latentsNums[-1] + cardinality)
    
    for i in range(1, len(latentsNums)):
        expr = 0
        for var in range(latentsNums[i - 1], latentsNums[i]):
            expr += q_min[var]
        model_min.addConstr(expr == 1.0)
    
    # Solve the minimization problem
    model_min.optimize()
    if model_min.Status == GRB.OPTIMAL: # OPTIMAL
        lower = model_min.objVal
        print(f"Minimal solution found!\nMIN Query: {lower}")
    else:
        print(f"Minimal solution not found. Gurobi status code: {model_min.Status}")
        lower = 0
    return lower


def noExplicitMechanisms():
    # s1: 1 <= P(!X | !U1 and !U2 and !Z) <= 1
    # s2: 1 <= P(!X | !U1 and !U2 and Z) <= 1
    # s3: 1 <= P(!X | !U1 and U2 and !Z) <= 1
    # s4: 1 <= P(X | !U1 and U2 and Z) <= 1
    # s5: 1 <= P(X | U1 and !U2 and !Z) <= 1
    # s6: 1 <= P(!X | U1 and !U2 and Z) <= 1
    # s7: 1 <= P(X | U1 and U2 and !Z) <= 1
    # s8: 1 <= P(X | U1 and U2 and Z) <= 1

    # s9: 1 <= P(!Y | !U3 and !U4 and !X) <= 1
    # s10: 1 <= P(!Y | !U3 and !U4 and X) <= 1
    # s11: 1 <= P(!Y | !U3 and U4 and !X) <= 1
    # s12: 1 <= P(Y | !U3 and U4 and X) <= 1
    # s13: 1 <= P(Y | U3 and !U4 and !X) <= 1
    # s14: 1 <= P(!Y | U3 and !U4 and X) <= 1
    # s15: 1 <= P(Y | U3 and U4 and !X) <= 1
    # s16: 1 <= P(Y | U3 and U4 and X) <= 1



    # Load your dataset
    data = pd.read_csv("balke_pearl.csv")  # Replace with your actual dataset path
    #  Group by Z, D, and T and count occurrences
    joint_frequencies = data.groupby(['Z', 'D', 'T']).size().reset_index(name='count')

    # Total number of observations
    total_count = joint_frequencies['count'].sum()

    # Add a column for the empirical probabilities
    joint_frequencies['probability'] = joint_frequencies['count'] / total_count

    # Create a dictionary for the empirical distribution
    empirical = {
        (row['Z'], row['X'], row['T']): row['probability']
        for _, row in joint_frequencies.iterrows()
    }


    # Initialize model
    model = Model("IV_Causal_Inference")
    z_vals = (0, 1)
    d_vals = (0, 1)
    t_vals = (0, 1)

    # Variables: probabilities for P(Z, D, T), P(T|D), P(D|Z)
    P_ZDT = model.addVars([z_vals, d_vals, t_vals], lb=0, ub=1, name="P_ZDT")
    P_T_given_D = model.addVars([d_vals, t_vals], lb=0, ub=1, name="P_T_given_D")
    P_D_given_Z = model.addVars([z_vals, d_vals], lb=0, ub=1, name="P_D_given_Z")

    # Compute P(Z=z) from empirical joint distribution
    P_Z = {}

    for (z, d, t), prob in empirical.items():
        if z not in P_Z:
            P_Z[z] = 0
        P_Z[z] += prob

    # Constraints: normalization
    for z in z_vals:
        model.addConstr(sum(P_D_given_Z[z, d] for d in d_vals) == 1)
    for d in d_vals:
        model.addConstr(sum(P_T_given_D[d, t] for t in t_vals) == 1)
    model.addConstr(sum(P_ZDT[z, d, t] for z in z_vals for d in d_vals for t in t_vals) == 1)

    # Constraints: marginal and conditional relations
    for z in z_vals:
        for d in d_vals:
            for t in t_vals:
                model.addConstr(P_ZDT[z, d, t] == P_D_given_Z[z, d] * P_T_given_D[d, t] * P_Z[z])

    # Objective: minimize squared error
    objective = sum((P_ZDT[z, d, t] - empirical[z, d, t])**2 for z in z_vals for d in d_vals for t in t_vals)
    model.setObjective(objective, GRB.MINIMIZE)

    # Solve the model
    model.optimize()

    # Extract results
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found")
        causal_effects = {d: P_T_given_D[d].X for d in d_vals}
