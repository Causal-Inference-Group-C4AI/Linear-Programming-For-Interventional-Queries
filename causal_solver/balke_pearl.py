from partition_methods.relaxed_problem.python.graph import Graph
from scipy.optimize import linprog

class balkePearl:
    def __init__(self, graph: Graph):
        self.graph = graph
    
def test():
    # Coeficientes da função objetivo
    c = [-1, 4]  # Exemplo: minimizar -x + 4y

    # Coeficientes das inequações (Ax <= b)
    A_ineq = [
        [-3, 1],
        [1, 2]
    ]
    
    b_ineq = [6, 4]

    # Coeficientes das equações (Ax = b)
    A_eq = [[1, 1]]
    b_eq = [3]

    # Chamada ao solver
    result = linprog(c, A_ub=A_ineq, b_ub=b_ineq, A_eq=A_eq, b_eq=b_eq, method="highs", bounds=(None,None))

    # Verificar o resultado
    if result.success:
        print("Solução ótima encontrada:", result.x)
        print("Valor da função objetivo:", result.fun)
    else:
        print("Solução não encontrada:", result.message)


def main():
    """
    Balke & Pearl IV example: code all the restrictions and try to use a linear solver.
    """

    """
    Variables:
    q00, q01, q02, q03, q10, q11, q12, q13, q20, q21, q22, q23, q30, q31, q32, q33.
    """

    c = [0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, 0] # obj
    negC = [-x for x in c]

    # Coeficientes das inequações (Ax <= b)    

    bounds2 = [(0, 1) for _ in range(16)]

    # Coeficientes das equações (Ax = b)
    A_eq = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1]
            ]
    
    b_eq = [1, 0.32, 0.32, 0.04, 0.32, 0.02, 0.17, 0.67, 0.14]

    result = linprog(c, A_ub=None, b_ub=None, A_eq=A_eq, b_eq=b_eq, method="highs", bounds=bounds2)
    resultNeg = linprog(negC, A_ub=None, b_ub=None, A_eq=A_eq, b_eq=b_eq, method="highs", bounds=bounds2)

    # Verificar o resultado
    if result.success:
        print("Solução ótima encontrada:", result.x)
        print("Valor da função objetivo:", result.fun)
    else:
        print("Solução não encontrada:", result.message)

    # Verificar o resultado neg
    if result.success:
        print("Solução ótima encontrada:", resultNeg.x)
        print("Valor da função objetivo:", -resultNeg.fun)
    else:
        print("Solução não encontrada:", resultNeg.message)

if __name__ == "__main__":
    main()