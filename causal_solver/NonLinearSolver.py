import pyomo.environ  as pyo
from collections import namedtuple
from causal_solver.NonLinearConstraints import *
from pyomo.opt import SolverFactory

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


def createModel(objective : dict[str, float], constraints : list[equationsObject], setU: list[int],
            cardinalities: dict[int,int], initVal: float = .5):
    
    numVar = 0
    
    model = pyo.ConcreteModel()
    for index in setU:
        numVar += cardinalities[index]
    
    model.q = pyo.Var(list(range(1, numVar + 1)), bounds=(0,1), initialize = initVal)
    model.eqConstrain = pyo.ConstraintList()
    expr = 0
    
    for key in objective:
        coef = objective[key]
        unobs = dictKey_to_index(key= key)
        
        if coef > 0:
            aux = coef
            for u in unobs:
                aux *= model.q[u]
            expr += aux
    
    model.obj = pyo.Objective(expr= expr)
     
    for eqn in constraints:
        expr = 0
        for key in eqn.dictionary:
          coef = eqn.dictionary[key]
          unobs = dictKey_to_index(key= key)
          if coef > 0:         
                aux = coef
                for u in unobs:
                    aux *= model.q[u]
                expr += aux
        model.eqConstrain.add(expr = eqn.probability)

    return model

if __name__ == "__main__":
    objectFun = itauTest()
    model = createModel(objective= objectFun, constraints= [],)
    print()