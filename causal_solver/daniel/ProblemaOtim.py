class ProblemaOtim:
    def __init__(self, mechanisms, variables, data, important_observables, intervention_dict) -> None:
        self.mechanisms = mechanisms
        self.gurobi_variables = variables # Cria aqui as variaveis do gurobi
        self.data = data
        self.important_observables = important_observables # vars que entram no problema de otim
        self.intervention_dict = {"A": 1, "C": 1}

        self.V = [i for i in range(8)]
        self.U = [i for i in range(8)]

    def objective_function(self):
        # U, V, B, D Sum( P(Y=1 | B, D) . P(B | U, A) . P(D | V, C) . P(U) P(V))
        #                 \----v------/   \-----------v-----------/  \----v------/
        #                    FROM DATA           MECHANISMS             VARIABLES (8 FROM U AND 8 FROM V)

        doA = self.intervention_dict["A"]
        doC = self.intervention_dict["C"]

        P_Y_given_B_D = {(1.0, 0.0, 1.0): 0.450,
                        (0.0, 0.0, 0.0): 0.124,
                        (0.0, 1.0, 1.0): 0.350,
                        (0.0, 1.0, 0.0): 0.076}

        expression = 0 # É de um tipo do Gurobi
        B = (0, 1)
        D = (0, 1)
        for b in B:
            for d in D:
                for u in self.U:
                    qual_B = self.mechanisms[u, doA]
                    if (b == qual_B):
                        for v in self.V:
                            expre_term = 1 # tipo Gurobi
                            qual_D = self.mechanisms[v, doC]
                            if (b == qual_B) and (d == qual_D):
                                # Pode não ser binário em outro contexto, assim (B == qual_B) and (D == qual_D) daria outros valores
                                expre_term *= self.data[P_Y_given_B_D[1, b, d]] * self.gurobi_variables[u] * self.gurobi_variables[v]
                            expression += expre_term
        return expression

    def constrainsts_builder(self):
        pass


    def mechanismListGenerator(cardinalities: dict[int, int], listUnob: list[int], setS: set[int], graphNodes: list[Node]):
        mechanismDictsList: list[list[dictAndIndex]] = [] # Same order as in listU
        globalIndex: int = 0
        latentCardinalities: dict[int, int] = {}
        for latentVariable in listUnob:
            endogenousInS: list[int] = list(set(graphNodes[latentVariable].children) & setS)
            _, _, mechanismDicts = Helper.mechanisms_generator(latentNode=latentVariable, endogenousNodes=endogenousInS,
                                            cardinalities=cardinalities,graphNodes=graphNodes,v=False)

            mechanismIndexDict: list[dictAndIndex] = []
            initVal: int = globalIndex
            for mechanismDict in mechanismDicts:
                mechanismIndexDict.append(dictAndIndex(mechanismDict, globalIndex))
                globalIndex += 1

            latentCardinalities[latentVariable] = globalIndex - initVal
            mechanismDictsList.append(mechanismIndexDict)

        return mechanismDictsList, latentCardinalities