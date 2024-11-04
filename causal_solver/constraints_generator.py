## TODO:
# 1 - para cada elemento de allPossibleMechanisms gerar um dicionario que leva a realizacao do domino
# (todos os elementos menos o ultimo) na imagem (ultimo elemento).
# 0 - Para isso precisa de um "header" que explicita qual a realizacao do domino e qual eh a variavel da 
# imagem em cada elemento. Fazer no preproecessamento esse header comum.

from partition_methods.relaxed_problem.python.graph import Graph
import itertools

class solver_middleware:
    def __init__(self, graph: Graph):
        self.graph = graph    
    
    """
    Por enquanto, para apenas uma c-component.
    """
    def empirical_constraints(latentNode: int, endogenousNodes: list[int], cardinalities: dict[int, int], parentsDict: dict[int, list[int]]):
        # (i) truth tables and the number of parameters        
        auxSpaces: list[list[int]] = []
        headerArray: list[str] = []
        allCasesList: list[list[list[int]]] = []
        for var in endogenousNodes:
            auxSpaces.clear()
            header: str = f"determines variable: {var}"
            amount: int = 1
            for parent in parentsDict[var]:
                if parent != latentNode:
                    header = f"{parent}, " + header
                    auxSpaces.append(range(cardinalities[parent]))
                    amount *= cardinalities[parent]

            headerArray.append(header + f" (x {amount})")
            functionDomain: list[list[int]] = [list(auxTuple) for auxTuple in itertools.product(*auxSpaces)]
            # print(functionDomain)

            # Valores possíveis para c
            imageValues: list[int] = range(cardinalities[var])            
            
            varResult = [[domainCase + [c] for c in imageValues] for domainCase in functionDomain]
            print(varResult)            
            allCasesList  = allCasesList + varResult
        
        print(headerArray)
        print(f"Lista com todos os mecanismos possíveis, agrupando os excludentes em um mesmo vetor:\n{allCasesList}")
        # Fazer um array de strings para podermos consultar qual a funcao (e o caso do dominio) abordado. Acho que pode valer a pena 
        # usar dicionario, porque precisaremos ficar consultando isso na hora de checar os mecanismos.

        allPossibleMechanisms = list(itertools.product(*allCasesList))
        for index, case in enumerate(allPossibleMechanisms):
            print(f"{index}) {case}")

    # Plano:
    # Adicionar gerador de mecanismos (listas de tabela verdade)
    # Cada u eh formado por uma combinacao de mecanismos. Assim, selecionamos 1 de cada tabela verdade
    # e todas essas combinacoes geram o conjunto de us.
    # As constraints sao da forma P(endogenasCcomponent | endogenas pais de endogenas do cComponent)
    # logo, o total de constraints equivale ao produto entre a dimensao dos espaços de cada variavel
    # endogena do c-component, o que eh menor que o numero de variaveis.

def main():    
    solver_middleware.empirical_constraints(0, [3, 6], {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {3: [0, 1, 2], 6: [0, 4, 5] })

if __name__ == "__main__":
    main()
