from itertools import product
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from causal_reasoning.utils._enum import Examples
from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper as ph

BIG_M = 1e4

class MasterProblem:
    def __init__(self):
        self.model = gp.Model("master")
        self.vars = None
        self.constrs = None
        
    def setup(self, columns_base: list[list[int]], empiricalProbabilities: list[float]):
        num_columns_base = len(columns_base)
        self.vars = self.model.addVars(num_columns_base, obj=BIG_M, name="BaseColumns") # obj = coefficient in the objective function.
        self.constrs = self.model.addConstrs((gp.quicksum(columns_base[column_id][realization_id] * self.vars[column_id]
                                                          for column_id in range(num_columns_base))
                                              == empiricalProbabilities[realization_id] for realization_id in range(len(empiricalProbabilities))),
                                             name="EmpiricalRestrictions")
        self.model.modelSense = GRB.MINIMIZE # The master problem should minimize the objective function.
        # Turning off output because of the iterative procedure
        self.model.params.outputFlag = 0
        self.model.update() # Use the gurobi built in update.
            
    def update(self, newColumn, index, objCoeff):        
        new_col = gp.Column(coeffs=newColumn, constrs=self.constrs.values()) # Includes the new variable in the constraints.
        #print(f"Obj coeff: {objCoeff}")
        # #print(f"new_col: {new_col}")
        self.vars[index] = self.model.addVar(obj=objCoeff, column=new_col, # Adds the new variable
                                             name=f"Variable[{index}]")
        self.model.update()

class SubProblem:
    def __init__(self):
        self.model = gp.Model("subproblem")
        self.bit_vars = {}
        self.auxiliary_vars = {}
        self.constr = None
        
    def setup(self, amountBits: int, duals: list[float], subproblemBitsCosts: list[float], amountRestrictions: int,
              parametric_columns: dict[str, tuple[list[int]]]):
        self.bit_vars = self.model.addVars(amountBits, obj=subproblemBitsCosts, vtype=GRB.BINARY,
                                       name=["b0", "b1", "b2", "b3", "b4"]) # b0, b1, b2, b3, b4.
        self.auxiliary_vars = self.model.addVars(amountRestrictions, obj=[-dualCost for dualCost in duals], vtype=GRB.BINARY,
                                       name=["au0", "au1", "au2", "au3", "au4", "au5", "au6", "au7"])

        for index, key in enumerate(parametric_columns):
            self.model.addConstr(self.auxiliary_vars[index] >= 0,
                                        name="IntegerProgrammingRestrictions")
            self.model.addConstr(self.auxiliary_vars[index] <= 1,
                                        name="IntegerProgrammingRestrictions")
            for bitPlus in parametric_columns[key][0]:                
                self.model.addConstr(self.auxiliary_vars[index] <= self.bit_vars[bitPlus],
                                        name="IntegerProgrammingRestrictions")
            for bitMinus in parametric_columns[key][1]:                
                self.model.addConstr(self.auxiliary_vars[index] <= 1 - self.bit_vars[bitMinus],
                                        name="IntegerProgrammingRestrictions")                        
            
        self.constrs = self.model.addConstrs(( gp.quicksum(self.bit_vars[bitPlus]
                                                    for bitPlus in parametric_columns[key][0]) +
                                                gp.quicksum(1 - self.bit_vars[bitMinus]
                                                    for bitMinus in parametric_columns[key][1]) +
                                                1 - (len(parametric_columns[key][0]) + len(parametric_columns[key][1]))
                                            <= self.auxiliary_vars[index] for index, key in enumerate(parametric_columns)), name="IntegerProgrammingRestrictions")
        
        self.model.modelSense = GRB.MINIMIZE
        # Turning off output because of the iterative procedure
        self.model.params.outputFlag = 0
        # Stop the subproblem routine as soon as the objective's best bound becomes
        #less than or equal to one, as this implies a non-negative reduced cost for
        #the entering column.
        self.model.params.bestBdStop = 1
        self.model.update()
        
    def update(self, duals):
        '''
        Change the objective functions coefficients.
        '''
        self.model.setAttr("obj", self.auxiliary_vars, [-duals[dual] for dual in duals])
        self.model.update()

class ItauProblem:
    def __init__(self, dataFrame, empiricalProbabilities, parametric_columns):
        self.amount_restrictions = 8
        self.columns_base = None
        self.empiricalProbabilities: list[float] = empiricalProbabilities
        self.amountBits = None
        # Order: (d,x,y)
        self.parametric_columns: dict[str, tuple[list[int]]] = parametric_columns # Ex: (d=1,x=0,y=1), "101" -> ([2],[0]) (L+, L-).        
        self.dataFrame = dataFrame
        prob1 = ph.find_conditional_probability2(dataFrame=dataFrame, targetRealization={"D": 0}, conditionRealization={"X": 1})
        prob2 = ph.find_conditional_probability2(dataFrame=dataFrame, targetRealization={"D": 1}, conditionRealization={"X": 1})
        self.subproblemBitsCosts = [0, 0, 0, prob1, prob2]

        self.duals = [0] * self.amount_restrictions
        self.solution = {}
        self.master = MasterProblem()
        self.subproblem = SubProblem()

    def _initialize_column_base(self):
        # Initialize big-M problem with the identity block of size
        # equal to the amount of restrictions.
        columns_base: list[list[int]] = []
        for index in range(self.amount_restrictions + 1):
            new_column = [0]*(self.amount_restrictions + 1)
            new_column[index] = 1
            columns_base.append(new_column)
        self.columns_base = columns_base

    def _generate_patterns(self):
        self._initialize_column_base()        
        self.master.setup(self.columns_base, self.empiricalProbabilities)        
        self.subproblem.setup(amountBits=5, duals=self.duals, subproblemBitsCosts=self.subproblemBitsCosts, amountRestrictions=8,
                              parametric_columns=self.parametric_columns)
        while True:
            self.master.model.optimize()
            self.duals = self.master.model.getAttr("pi", self.master.constrs)
            #print(f"Master Duals: {self.duals}")
            # self.master.model.write(f"master_{i}.lp")
            self.subproblem.update(self.duals)
            self.subproblem.model.optimize()
            # self.subproblem.model.write(f"subproblem_{i}.lp")
            reduced_cost = self.subproblem.model.objVal
            #print(f"Reduced Cost: {reduced_cost}")
            if reduced_cost >= 0:
                break
            
            # TODO
            # pattern = [0]*len(self.pieces)
            # for piece, var in self.subproblem.vars.items():
            #     if var.x > 0.5:
            #         pattern[piece] = round(var.x)
            
            # Calculate the column
            newColumn: list[int] = []
            for key in self.parametric_columns:
                currentValue = 1
                for bitPlus in self.parametric_columns[key][0]:
                    if self.subproblem.bit_vars[bitPlus].X == 0:
                        currentValue = 0; break
                
                for bitMinus in self.parametric_columns[key][1]:
                    if self.subproblem.bit_vars[bitMinus].X == 1:
                        currentValue = 0; break
                newColumn.append(currentValue)
            newColumn.append(1) # For the equation sum(pi) = 1
            #print(f"New Column: {newColumn}")
            # Calculate obj. function:
            objCoeff: float = self.subproblemBitsCosts[3] * self.subproblem.bit_vars[3].X + self.subproblemBitsCosts[4] * self.subproblem.bit_vars[4].X
            self.master.update(newColumn=newColumn, index=len(self.columns_base), objCoeff=objCoeff)
            self.columns_base.append(newColumn)
            ### ###

    def solve(self):
        """
        Gurobi does not support branch-and-price, as this requires to add columns
        at local nodes of the search tree. A heuristic is used instead, where the
        integrality constraints for the variables of the final root LP relaxation
        are installed and the resulting MIP is solved. Note that the optimal
        solution could be overlooked, as additional columns are not generated at
        the local nodes of the search tree.
        """
        self._generate_patterns()
        self.master.model.setAttr("vType", self.master.vars, GRB.CONTINUOUS) # useless?
        self.master.model.optimize()

        #print(f"Result of the inference: {self.master.model.ObjVal}")
        # for pattern, var in self.master.vars.items():
        #     if var.x > 0.5:
        #         self.solution[pattern] = round(var.x)

def main():
    itau_csv_path = Examples.CSV_ITAU_EXAMPLE.value; df = pd.read_csv(itau_csv_path)
    empiricalProbabilities: list[float] = []
    for realizationCase in list(product([0, 1], repeat=3)):
        targetRealization = {"Y": realizationCase[2]}
        conditionRealization = {"D": realizationCase[0], "X": realizationCase[1]}
        part1 = ph.find_conditional_probability2(dataFrame=df, targetRealization=targetRealization, conditionRealization=conditionRealization)        
        part2 = ph.find_probability2(dataFrame=df, realizationDict={"X": realizationCase[1]})
        empiricalProbabilities.append(part1 * part2)
        #print(f"EmpiricialProb[{realizationCase[0]}{realizationCase[1]}{realizationCase[2]} = {empiricalProbabilities[-1]}")
    empiricalProbabilities.append(1)

    # TODO: parametric_columns    
    parametric_columns = {
                        "000": ([], [0, 1]),
                        "001": ([1], [0]),
                        "010": ([0], [3]),
                        "011": ([0,3], []),
                        "100": ([], [0, 2]),
                        "101": ([2], [0]),
                        "110": ([0], [4]),
                        "111": ([0, 4], []),
    }
    itauProblem = ItauProblem(dataFrame=df, empiricalProbabilities=empiricalProbabilities, parametric_columns=parametric_columns)
    itauProblem.solve()

if __name__=="__main__":
    main()