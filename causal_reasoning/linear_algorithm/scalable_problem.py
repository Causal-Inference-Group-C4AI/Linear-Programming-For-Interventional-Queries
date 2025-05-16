from itertools import product
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from data_gen import generate_data_for_scale_case

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from causal_reasoning.utils._enum import Examples
from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper as ph

BIG_M = 1e4
N = 2
DBG = True

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
            
    # TODO: calcular coef objetivo da nova coluna.
    def update(self, newColumn, index, objCoeff):        
        new_col = gp.Column(coeffs=newColumn, constrs=self.constrs.values()) # Includes the new variable in the constraints.
        print(f"Obj coeff: {objCoeff}")
        # print(f"new_col: {new_col}")
        self.vars[index] = self.model.addVar(obj=objCoeff, column=new_col, # Adds the new variable
                                             name=f"Variable[{index}]")
        self.model.update()

class SubProblem:
    def __init__(self):
        self.model = gp.Model("subproblem")
        self.bit_vars = {}
        self.beta_vars = {}
        self.auxiliary_varsX0 = {}
        self.auxiliary_varsX1 = {}
        self.constr = None
        
    def setup(self, amountBits: int, amountBetaVars: int, duals: list[float], betaVarsCost: dict[str, float], amountNonTrivialRestrictions: int, parametric_columns: dict[str, tuple[list[int]]],
              betaVarsBits: list[tuple[list[str]]]):

        # ------------------
        names: list[str] = []
        for i in range(amountBits): names.append(f"b{i}")
        self.bit_vars = self.model.addVars(amountBits, obj=0, vtype=GRB.BINARY,
                                       name=names)

        betaVarNames: list[str] = []
        for i in range(amountBetaVars): betaVarNames.append(f"beta{i}")
        self.beta_vars = self.model.addVars(amountBetaVars, obj=betaVarsCost, vtype=GRB.BINARY,
                                       name=betaVarNames)

        
        # au variables for rows in which the X variable is 0 
        auxVarX0Names: list[str] = []
        for i in range(amountNonTrivialRestrictions // 2): auxVarX0Names.append(f"au0{i}")        
        self.auxiliary_varsX0 = self.model.addVars(amountNonTrivialRestrictions // 2, obj=[-dualCost for dualCost in duals[:len(duals) // 2]], vtype=GRB.BINARY,
                                       name=auxVarX0Names)

        # au variables for rows in which the X variable is 1
        auxVarX1Names: list[str] = []
        for i in range(amountNonTrivialRestrictions // 2): auxVarX1Names.append(f"au1{i}")
        self.auxiliary_varsX1 = self.model.addVars(amountNonTrivialRestrictions // 2, obj=[-dualCost for dualCost in duals[len(duals) // 2:]], vtype=GRB.BINARY,
                                       name=auxVarX1Names)

        
# ------ Beta Constraints
        for indexBetaVar in range(amountBetaVars):
            self.model.addConstr(self.beta_vars[indexBetaVar] >= 0,
                                        name=f"IntegerProgrammingRestrictionsBeta{indexBetaVar}")
            self.model.addConstr(self.beta_vars[indexBetaVar] <= 1,
                                        name=f"IntegerProgrammingRestrictionsBeta{indexBetaVar}")
            
            for bitPlus in betaVarsBits[indexBetaVar][0]:
                self.model.addConstr(self.beta_vars[indexBetaVar] <= self.bit_vars[bitPlus],
                                        name=f"IntegerProgrammingRestrictions{indexBetaVar}BitPlus{bitPlus}")
            for bitMinus in betaVarsBits[indexBetaVar][1]:
                self.model.addConstr(self.beta_vars[indexBetaVar] <= 1 - self.bit_vars[bitMinus],
                                        name=f"IntegerProgrammingRestrictions{indexBetaVar}BitMinus{bitMinus}")
                
        # 1 - N + sum(b+) + sum(1 - b-) <= beta
        self.constrs = self.model.addConstrs(( gp.quicksum(self.bit_vars[bitPlus]
                                                for bitPlus in betaVarsBits[indexBetaVar][0]) +
                                            gp.quicksum(1 - self.bit_vars[bitMinus]
                                                for bitMinus in betaVarsBits[indexBetaVar][1]) +
                                            1 - (len(betaVarsBits[0]) + len(betaVarsBits[1]))
                                        <= self.beta_vars[index] for index in range(len(self.beta_vars))), name="BetaForce1Condition")
# ------ ------
# ------ ------
        # TODO: check if the indexes of betaVars and each half of auxVars match        
        for indexAuxVar0 in range(amountNonTrivialRestrictions // 2):
            self.model.addConstr(self.auxiliary_varsX0[indexAuxVar0] >= 0,
                                        name=f"IntegerProgrammingRestrictionsAux0{indexAuxVar0}")
            self.model.addConstr(self.auxiliary_varsX0[indexAuxVar0] <= 1,
                                        name=f"IntegerProgrammingRestrictionsAux0{indexAuxVar0}")
            
            self.model.addConstr(self.auxiliary_varsX0[indexAuxVar0] <= 1 - self.bit_vars[0],
                                        name=f"IntegerProgrammingRestrictionsAux0{indexAuxVar0}")
            
            self.model.addConstr(self.auxiliary_varsX0[indexAuxVar0] <= self.beta_vars[indexAuxVar0],
                                        name=f"IntegerProgrammingRestrictionsAux0{indexAuxVar0}")

            self.model.addConstr(self.beta_vars[indexAuxVar0] - self.bit_vars[0] <= self.auxiliary_varsX0[indexAuxVar0],
                                        name=f"IntegerProgrammingRestrictionsAux0{indexAuxVar0}")
        
        for indexAuxVar1 in range(amountNonTrivialRestrictions // 2):
            self.model.addConstr(self.auxiliary_varsX1[indexAuxVar1] >= 0,
                                        name=f"IntegerProgrammingRestrictionsAux1{indexAuxVar1}")
            self.model.addConstr(self.auxiliary_varsX1[indexAuxVar1] <= 1,
                                        name=f"IntegerProgrammingRestrictionsAux1{indexAuxVar1}")
            
            self.model.addConstr(self.auxiliary_varsX1[indexAuxVar1] <= self.bit_vars[0],
                                        name=f"IntegerProgrammingRestrictionsAux1{indexAuxVar1}")
            
            self.model.addConstr(self.auxiliary_varsX1[indexAuxVar1] <= self.beta_vars[indexAuxVar1],
                                        name=f"IntegerProgrammingRestrictionsAux1{indexAuxVar1}")

            self.model.addConstr(self.beta_vars[indexAuxVar1] + self.bit_vars[0] <= self.auxiliary_varsX1[indexAuxVar1] + 1,
                                        name=f"IntegerProgrammingRestrictionsAux1{indexAuxVar1}")
        
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
        # First half of restrictions have X=0, second half have X=1.
        self.model.setAttr("obj", self.auxiliary_varsX0, [-duals[dual] for dual in duals[:len(duals) // 2]])
        self.model.setAttr("obj", self.auxiliary_varsX1, [-duals[dual] for dual in duals[len(duals) // 2:]])
        self.model.update()

class ItauProblem:
    def __init__(self, dataFrame, empiricalProbabilities: list[float], parametric_columns: dict[str, tuple[list[int]]], N: int, betaVarsCost: list[float]):
        self.amountNonTrivialRestrictions = (1 << (N + 1))
        self.amountBits = 2 * N + 1
        self.amountBetaVars = (1 << (2 * N))
        self.columns_base = None
        self.empiricalProbabilities: list[float] = empiricalProbabilities
        self.amountBits = None
        # Order parametric_columns key: (X B1 A1 B2 A2 .. BN AN)
        self.parametric_columns: dict[str, tuple[list[int]]] = parametric_columns
        self.dataFrame = dataFrame

        # Coeficientes da função objetivo.        
        self.betaVarsCost = betaVarsCost

        self.duals = [0] * self.amountNonTrivialRestrictions
        self.solution = {}
        self.master = MasterProblem()
        self.subproblem = SubProblem()

    def _initialize_column_base(self):
        # Initialize big-M problem with the identity block of size
        # equal to the amount of restrictions.
        columns_base: list[list[int]] = []
        for index in range(self.amountNonTrivialRestrictions + 1):
            new_column = [0]*(self.amountNonTrivialRestrictions + 1)
            new_column[index] = 1
            columns_base.append(new_column)
        self.columns_base = columns_base

    def _generate_patterns(self):
        self._initialize_column_base()        
        self.master.setup(self.columns_base, self.empiricalProbabilities)        
        self.subproblem.setup(amountBits=self.amountBits, amountBetaVars=self.amountBetaVars, duals=self.duals, amountNonTrivialRestrictions=self.amountNonTrivialRestrictions,
                              parametric_columns=self.parametric_columns, betaVarsCost=self.betaVarsCost,
                              betaVarsBits=self.betaVars)

        while True:
            self.master.model.optimize()
            self.duals = self.master.model.getAttr("pi", self.master.constrs)
            print(f"Master Duals: {self.duals}")
            # self.master.model.write(f"master_{i}.lp")
            self.subproblem.update(self.duals)
            self.subproblem.model.optimize()
            # self.subproblem.model.write(f"subproblem_{i}.lp")
            reduced_cost = self.subproblem.model.objVal
            print(f"Reduced Cost: {reduced_cost}")
            if reduced_cost >= 0:
                break

            
            # TODO: To get the new column, we can just use the aux vars! Change the current logic.
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
            print(f"New Column: {newColumn}")
            # Calculate obj. function:

            #  latentRealization = (self.subproblemBitsCosts[0].X,....,)
            #  objCoeff = pegaCoeficiente(latentRealization)
            # (latentRealization, Probabilities: [(dict[str: int], dict[str: int])], Mechanisms: [(str, int, dict[str, int])])
            # [(Y, 1, {X: 1, D: 0})])

            # TODO: Use _getCoefficient method to find the coeff of the new column in the obj of the master
            objCoeff: float = self.subproblemBitsCosts[3] * self.subproblem.bit_vars[3].X + self.subproblemBitsCosts[4] * self.subproblem.bit_vars[4].X
            self.master.update(newColumn=newColumn, index=len(self.columns_base), objCoeff=objCoeff)
            self.columns_base.append(newColumn)

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

        print(f"Result of the inference: {self.master.model.ObjVal}")

def main():    
    itau_csv_path = Examples.CSV_2SCALING.value; df = pd.read_csv(itau_csv_path)
    interventionValue = 0; targetValue = 0
    
    
# Calculate the empirical probs (RHS of the restrictions, so b in Ax=b)
# ----------------
    empiricalProbabilities: list[float] = []
    setCurrentVars: set[str] = {"X"}
    for i in range(1,N + 1):
        setCurrentVars.update({f"A{i}", f"B{i}"})

    for realizationCase in list(product([0, 1], repeat= 2 * N + 1)):
        currentProbability: float = ph.find_probability2(dataFrame=df, realizationDict={ "X": realizationCase[0]})
        for i in range(N, 0, -1):
            targetRealization = {f"A{i}": realizationCase[2 * i]}
            if (i == N):
                setCurrentVars.remove(f"A{i}")
            else:
                setCurrentVars.remove(f"A{i}")
                setCurrentVars.remove(f"B{i + 1}")
                
            conditionRealization: dict[str, int] = {}
            for var in setCurrentVars:
                if var == "X":
                    index = 0
                elif var[0] == "A":
                    index = 2 * i
                elif var[0] == "B":
                    index = 2 * i - 1                    
                
                conditionRealization[var] = realizationCase[index]

            currentProbability *= ph.find_conditional_probability2(dataFrame=df, 
                                                                   targetRealization=targetRealization, 
                                                                   conditionRealization=conditionRealization)            
        
        empiricalProbabilities.append(currentProbability)            
        if DBG: print(f"Calculated empirical prob: {empiricalProbabilities[-1]}")
    
    empiricalProbabilities.append(1)

    
# Calculate the beta vars obj coeff in the subproblem and the relation to the bit variables
# ----------------    
    betaVarsBits: list[tuple[list[str]]] = [0] * (1 << (2 * N))
    betaVarsCoeffObjSubproblem: list[float] = [0] * (1 << (2 * N))

    bitPlus: list[int] = []
    bitMinus: list[int] = []
    for i, realizationCase in enumerate(list(product([0, 1], repeat= 2 * N))):
        betaVarIndex = i

        # Determines B+ and B- sets for each beta var
        for i in range(1, N + 1):
            currentAValue = realizationCase[2 * i - 1]
            currentBValue = realizationCase[2 * i - 2]

            if   (currentBValue == 0 and currentAValue == 0):
                bitIndex = 2 * i - 1
                bitMinus.append(str(bitIndex))
            elif (currentBValue == 0 and currentAValue == 1):
                bitIndex = 2 * i - 1
                bitPlus.append(str(bitIndex))
            elif (currentBValue == 1 and currentAValue == 0):
                bitIndex = 2 * i
                bitMinus.append(str(bitIndex))
            elif (currentBValue == 1 and currentAValue == 1):
                bitIndex = 2 * i
                bitPlus.append(str(bitIndex))
        
        betaVarsBits[betaVarIndex] = (bitPlus.copy(), bitMinus.copy())
        bitPlus.clear(); bitMinus.clear()
        # -------------

        # Calculates the coeff of each beta in the objective function of the subproblem
        currCoeff: float = ph.find_conditional_probability2(dataFrame=df,
                                                            targetRealization={"Y": targetValue},
                                                            conditionRealization={f"A{N}": realizationCase[2 * N - 1]})
        
        for i in range(1, N + 1):
            #P(Bi|A{i-1}), A0 = X
            if (i == 1): conditionRealization = {"X": interventionValue}
            else: conditionRealization = {f"A{i-1}": realizationCase[2 * (i - 1) - 1]}
            
            currCoeff *= ph.find_conditional_probability2(dataFrame=df, 
                                                          targetRealization={f"B{i}"},
                                                          conditionRealization=conditionRealization)

        betaVarsCoeffObjSubproblem[betaVarIndex] = currCoeff
# -----------------------
# -----------------------

    # Parametric_columns key: {xVal}beta{BetaVarIndex}
    parametric_columns: dict[str, tuple[list[str]]] = {}
    bitPlus: list[int] = []; bitMinus: list[int] = []
    for betaVarIndex in range(len(betaVarsBits)):
        for xRealization in range(0,2):
            completeKey = str(xRealization) + f"beta{betaVarIndex}" 
            bitPlus.append(f"b{betaVarIndex}")
            if xRealization == 0:
                bitMinus.append(0)
            else :
                bitPlus.append(0)
        
            parametric_columns[completeKey] = (bitPlus.copy(), bitMinus.copy())
        
    itauProblem = ItauProblem(dataFrame=df, empiricalProbabilities=empiricalProbabilities, parametric_columns=parametric_columns, N=N, betaVarsCost=betaVarsCoeffObjSubproblem, betaVarsBits=betaVarsBits)
                              
    itauProblem.solve()

if __name__=="__main__":
    generate_data_for_scale_case(N)
    main()
