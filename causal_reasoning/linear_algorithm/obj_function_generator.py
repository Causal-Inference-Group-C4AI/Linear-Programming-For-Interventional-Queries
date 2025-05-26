import argparse
import copy
import os
import logging

logger = logging.getLogger(__name__)

import pandas as pd

from causal_reasoning.graph.graph import Graph
from causal_reasoning.utils.mechanisms_generator import MechanismGenerator
from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper
import networkx as nx

class ObjFunctionGenerator:
    """
    Given an intervention and a graph, this class finds a set of restrictions that can be used to build
    a linear objective function.
    """

    def __init__(
        self,
        graph: Graph,
        intervention: int,
        target: int | str,
        intervention_value: int,
        target_value: int,
        dataFrame,
        empiricalProbabilitiesVariables: list[int],
        mechanismVariables: list[int],
        conditionalProbabilitiesVariables: dict[int, list[int]],
        debugOrder: list[int],
    ):
        """
        graph: an instance of the personalized class graph
        intervention: X in P(Y|do(X))
        intervention_value: the value assumed by the X variable
        target: Y in P(Y|do(X))
        """

        self.graph = graph
        self.intervention = intervention
        self.intervention_value = intervention_value
        self.target = target
        self.target_value = target_value
        self.dataFrame = dataFrame

        self.empiricalProbabilitiesVariables = empiricalProbabilitiesVariables
        self.mechanismVariables = mechanismVariables
        self.conditionalProbabilitiesVariables = conditionalProbabilitiesVariables
        self.debugOrder = debugOrder

    def find_linear_good_set(self):
        """
        Runs each step of the algorithm. Finds a set of variables/restrictions that linearizes the problem.
        """
        intervention: int = self.intervention
        current_targets: list[int] = [self.target]
        interventionLatent: int = self.graph.graphNodes[intervention].latentParent
    
        empiricalProbabilitiesVariables = (
            []
        )  # If V in this array then it implies P(v) in the objective function
        # If V in this array then it implies a decision function: 1(Pa(v) => v=
        # some value)
        mechanismVariables = []
        # If V|A,B,C in this array then it implies P(V|A,B,C) in the objective
        # function
        conditionalProbabilities: dict[int, list[int]] = {}
        debugOrder: list[int] = []

        # Create nx of the graph without outgoing edges of X:
        
        operatedDigraph = copy.deepcopy(self.graph.DAG)
        outgoing_edgesX = list(self.graph.DAG.out_edges(intervention))
        operatedDigraph.remove_edges_from(outgoing_edgesX)
        
        while len(current_targets) > 0:            
            logger.debug("---- Current targets array:")
            for tg in current_targets:
                logger.debug(f"- {self.graph.indexToLabel[tg]}")
            
            j = len(self.graph.topologicalOrder) - 1
            while (j >= 0):                
                if self.graph.topologicalOrder[j] in current_targets:
                    current_target = self.graph.topologicalOrder[j]                    
                    break
                j -= 1

            current_targets.remove(current_target)
            debugOrder.append(current_target)
            logger.debug(f"Current target: {self.graph.indexToLabel[current_target]}")

            if not self.graph.is_descendant(
                ancestor=self.intervention, descendant=current_target
            ):
                logger.debug(f"------- Case 1: Not a descendant")
                empiricalProbabilitiesVariables.append(current_target)
            elif (
                self.graph.graphNodes[current_target].latentParent == interventionLatent
            ):
                logger.debug(f"------- Case 2: Mechanisms")
                mechanismVariables.append(current_target)
                for parent in self.graph.graphNodes[current_target].parents:
                    # if (parent not in current_targets) and parent != intervention:
                    if (parent not in current_targets):
                        current_targets.append(parent)
            else:
                logger.debug(f"------- Case 3: Find d-separator set")
                ancestors = self.graph.find_ancestors(node=current_target)

                alwaysConditionedNodes: list[int] = current_targets.copy()
                if current_target in alwaysConditionedNodes:
                    alwaysConditionedNodes.remove(current_target)

                if interventionLatent in alwaysConditionedNodes:
                    alwaysConditionedNodes.remove(interventionLatent)
                
                conditionableAncestors: list[int] = []

                for ancestor in ancestors:                
                    if (
                        self.graph.cardinalities[ancestor] > 0
                        and ancestor != current_target
                        and ancestor not in alwaysConditionedNodes
                    ):
                        conditionableAncestors.append(ancestor)

                

                logger.debug("Always Conditioned ancestors:")
                for condNode in alwaysConditionedNodes:
                    logger.debug(f"{self.graph.indexToLabel[condNode]}")


                logger.debug("Conditionable ancestors:")
                for condNode in conditionableAncestors:
                    logger.debug(f"{self.graph.indexToLabel[condNode] } ")
                    
                
                failureFlag = True
                for x in range(pow(2, len(conditionableAncestors))):
                    conditionedNodes: list[int] = alwaysConditionedNodes.copy()
                    for i in range(len(conditionableAncestors)):
                        if (x >> i) % 2 == 1:
                            conditionedNodes.append(conditionableAncestors[i])
                
                    condition1 = nx.is_d_separator(G=self.graph.DAG, x= { current_target }, y = { interventionLatent }, z = set(conditionedNodes))
                    if intervention in conditionedNodes:
                        condition2 = True
                    else:
                        condition2 = nx.is_d_separator(G=operatedDigraph, x = {current_target}, y = {intervention}, z = set(conditionedNodes))

                    if condition1 and condition2:
                        separator: list[int] = []
                        logger.debug(f"The following set works:")
                        for element in conditionedNodes:
                            logger.debug(f"{self.graph.indexToLabel[element]} ", end="")
                            separator.append(element)               
                        logger.debug("\n")         
                        
                        failureFlag = False; break

                if failureFlag: logger.error("Failure: Could not find a separator set")
                
                current_targets = list(
                    (set(current_targets) | set(separator))                    
                    - {current_target}
                )
                
                conditionalProbabilities[current_target] = separator
                
        self.empiricalProbabilitiesVariables = empiricalProbabilitiesVariables
        self.mechanismVariables = mechanismVariables
        self.conditionalProbabilities = conditionalProbabilities
        self.debugOrder = debugOrder
        logger.debug("Found linear good set")

    def get_mechanisms_pruned(self) -> list[list[int]]:
        """
        Remove c-component variables that do not appear in the objective function
        """
        interventionLatentParent = self.graph.graphNodes[self.intervention].latentParent
        cComponentEndogenous = self.graph.graphNodes[interventionLatentParent].children

        endogenousNodes = (set(cComponentEndogenous) & set(self.debugOrder)) | {
            self.intervention
        }

        _, _, mechanisms = MechanismGenerator.mechanisms_generator(
            latentNode=interventionLatentParent,
            endogenousNodes=endogenousNodes,
            cardinalities=self.graph.cardinalities,
            graphNodes=self.graph.graphNodes,
            v=False,
        )
        return mechanisms

    def build_objective_function(self, mechanisms: list[list[int]]) -> list[float]:
        """
        Intermediate step: remove useless endogenous variables in the mechanisms creation?
        Must be called after generate restrictions. Returns the objective function with the following encoding

        For each mechanism, find the coefficient in the objective function.
            Open a sum on this.debugOrder variables <=> consider all cases (cartesian product).
            Only the intervention has a fixed value.
        """
        
        logger.debug(f"Debug variables: {self.debugOrder}")
        if self.intervention in self.debugOrder:
            self.debugOrder.remove(self.intervention)

        summandNodes = list(
            set(self.debugOrder)
            - {
                self.intervention,
                self.graph.graphNodes[self.intervention].latentParent,
                self.target,
            }
        )

        spaces: list[list[int]] = MechanismGenerator.helper_generate_spaces(
            nodes=summandNodes, cardinalities=self.graph.cardinalities
        )
        summandNodes.append(self.target)
        spaces.append([self.target_value])
        inputCases: list[list[int]] = MechanismGenerator.generate_cross_products(
            listSpaces=spaces
        )
        """
        TODO: Check the order of "inputCases": it should be the same as the order of the spaces, which is the same as in debugOrder.
        TODO: the case in which the summandNodes is empty (e.g Balke Pearl) has a very ugly fix
        """
        objFunctionCoefficients: list[float] = []
        logger.debug("Debug input cases:")
        logger.debug(f"Size of #inputs: {len(inputCases)}")
        logger.debug(f"first component:")
        logger.debug(inputCases[0])
        logger.debug("Debug summand nodes")
        for node in summandNodes:
            logger.debug(f"index={node}, label={self.graph.indexToLabel[node]}")

        logger.debug("--- DEBUG OBJ FUNCTION GENERATION ---")
        for mechanism in mechanisms:
            logger.debug("-- START MECHANISM --")
            mechanismCoefficient: int = 0
            for inputCase in inputCases:
                logger.debug("---- START INPUT CASE ----")
                variablesValues: dict[int, int] = {
                    self.intervention: self.intervention_value,
                    self.target: self.target_value,
                }
                partialCoefficient = 1

                for index, variableValue in enumerate(inputCase):
                    variablesValues[summandNodes[index]] = variableValue
                    logger.debug(f"{self.graph.indexToLabel[summandNodes[index]]} = {variableValue}")

                for variable in summandNodes:
                    logger.debug(
                        f"\nCurrent variable: {self.graph.indexToLabel[variable]} (index={variable})"
                    )
                    if (
                        variable in self.empiricalProbabilitiesVariables
                    ):  # Case 1: coff *= P(V=value)
                        logger.debug("Case 1")
                        variableProbability = ProbabilitiesHelper.find_probability(
                            dataFrame=self.dataFrame,
                            indexToLabel=self.graph.indexToLabel,
                            variableRealizations={variable: variablesValues[variable]},
                            v=False,
                        )
                        partialCoefficient *= variableProbability
                    elif (
                        variable in self.mechanismVariables
                    ):  # Case 2: terminate with coeff 0 if the decision function is 0. Do nothing otherwise
                        logger.debug("Case 2")
                        mechanismKey: str = ""
                        for nodeIndex, node in enumerate(self.graph.graphNodes):
                            if not node.isLatent and (variable in node.children):
                                mechanismKey += (
                                    f"{nodeIndex}={variablesValues[nodeIndex]},"
                                )
                        logger.debug(f"key: {mechanismKey[:-1]}")
                        expectedValue = mechanism[mechanismKey[:-1]]

                        if expectedValue != variablesValues[variable]:
                            partialCoefficient = 0
                            logger.debug("End process")
                    else:  # Case 3: coeff *= P(V|some endo parents)
                        logger.debug("Case 3")
                        conditionRealization: dict[int, int] = {}
                        for conditionalVariable in self.conditionalProbabilities[
                            variable
                        ]:
                            conditionRealization[conditionalVariable] = variablesValues[
                                conditionalVariable
                            ]

                        conditionalProbability = (
                            ProbabilitiesHelper.find_conditional_probability(
                                dataFrame=self.dataFrame,
                                indexToLabel=self.graph.indexToLabel,
                                targetRealization={variable: variablesValues[variable]},
                                conditionRealization=conditionRealization,
                                v=False,
                            )
                        )
                        partialCoefficient *= conditionalProbability

                    logger.debug(f"current partial coefficient: {partialCoefficient}")
                    if partialCoefficient == 0:
                        break

                mechanismCoefficient += partialCoefficient
                logger.debug(f"current coef = {mechanismCoefficient}")

            objFunctionCoefficients.append(mechanismCoefficient)


        logger.debug(f"\n\n-------- Debug restrictions --------")        
        for node in self.debugOrder:
            if node in self.empiricalProbabilitiesVariables:
                logger.debug(f"P({self.graph.indexToLabel[node]})")
            elif node in self.mechanismVariables:
                parents: str = ""
                for parent in self.graph.graphNodes[node].parents:
                    parents += f"{self.graph.indexToLabel[parent]}, "
                logger.debug(f"P({self.graph.indexToLabel[node]}|{parents[:-2]})")
            else:
                wset: str = ""
                for condVar in self.conditionalProbabilities[node]:
                    if condVar != self.intervention:
                        wset += f"{self.graph.indexToLabel[condVar]}, "
                logger.debug(
                    f"P({self.graph.indexToLabel[node]}|{self.graph.indexToLabel[self.intervention]}, {wset[:-2]})"
                )

            if node != self.debugOrder[-1]:
                logger.debug(" * ")

        logger.debug("\n")
        
        return objFunctionCoefficients

    def test(graph: Graph, csv_path):
        """
        used for the development of the class. Uses the itau graph itau.txt.
        """
        df = pd.read_csv(csv_path)

        objFG = ObjFunctionGenerator(
            graph=graph,
            intervention=graph.labelToIndex["X"],
            intervention_value=0,
            target=graph.labelToIndex["Y"],
            target_value=1,
            empiricalProbabilitiesVariables=[],
            mechanismVariables=[],
            conditionalProbabilitiesVariables={},
            debugOrder=[],
            dataFrame=df,
        )
        objFG.find_linear_good_set()
        logger.debug(f"\n\n-------- Debug restrictions --------")
        for node in objFG.debugOrder:
            if node in objFG.empiricalProbabilitiesVariables:
                logger.debug(f"P({objFG.graph.indexToLabel[node]})", end="")
            elif node in objFG.mechanismVariables:
                parents: str = ""
                for parent in objFG.graph.graphNodes[node].parents:
                    parents += f"{objFG.graph.indexToLabel[parent]}, "
                logger.debug(f"P({objFG.graph.indexToLabel[node]}|{parents[:-2]})", end="")
            else:
                wset: str = ""
                for condVar in objFG.conditionalProbabilities[node]:
                    if condVar != objFG.intervention:
                        wset += f"{objFG.graph.indexToLabel[condVar]}, "
                logger.debug(
                    f"P({objFG.graph.indexToLabel[node]}|{objFG.graph.indexToLabel[objFG.intervention]}, {wset[:-2]})",
                    end="",
                )

            if node != objFG.debugOrder[-1]:
                logger.debug(" * ", end="")

        logger.debug("\n")

        mechanisms = objFG.get_mechanisms_pruned()
        objCoefficients = objFG.build_objective_function(mechanisms)
        logger.debug("--- DEBUG OBJ FUNCTION ---")
        for i, coeff in enumerate(objCoefficients):
            logger.debug(f"c_{i} = {coeff}")
