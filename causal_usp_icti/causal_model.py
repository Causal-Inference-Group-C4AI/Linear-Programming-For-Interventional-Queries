import networkx as nx
from typing import Optional

from causal_usp_icti.utils.funcoes import get_tuple_edges
from causal_usp_icti.graph.graph import Graph
from pandas import DataFrame

class CausalModel:
    def __init__(
        self, 
        data: DataFrame,
        edges: str,
        unobservables: list[str],
        interventions: Optional[list[str]] = None,
        target: Optional[str] = None
    ) -> None:
            self._data = data
            self.unobservables = unobservables
            self.interventions = interventions
            self.target = target
            self.graph = input_processor()

    def visualize_graph(self):
        '''
            Create an image and plot the DAG
        '''
        # TODO: Implement in the class Graph
        raise NotImplementedError
    
    def add_interventions(self, interventions: list[str]) -> None:
        # TODO: verify if the nodes in intervention is in the graph (nodes list)
        for element in interventions:
            self.interventions.append(element)

    def set_interventions(self, interventions: list[str]) -> None:
        self.interventions = []
        self.add_interventions(interventions)
    
    def set_target(self, target: str) -> None:
        # TODO: verify if the 'target' node is in the graph (nodes list)
        self.target = target

def input_processor(edges_str: str, latents: list[str]) -> str:
    custom_cardinalities = {}

    edges_part = edges_str.split(",")
    edges = []
    node_order = []
    node_set = set()

    for part in edges_part:
        part = part.strip()
        left, right = part.split("->")
        left = left.strip()
        right = right.strip()

        edges.append((left, right))

        for n in (left, right):
            if n not in node_set:
                node_order.append(n)
                node_set.add(n)

    node_card = {}
    for node in node_order:
        if node in custom_cardinalities:
            node_card[node] = custom_cardinalities[node]
        else:
            node_card[node] = 0 if node in latents else 2

    u_nodes = [n for n in node_order if n in latents]
    other_nodes = [n for n in node_order if not n in latents]
    final_node_order = u_nodes + other_nodes


    lines = []

    lines.append(str(len(final_node_order))) # no nodes
    lines.append(str(len(edges))) #no edges

    for node in final_node_order:
        lines.append(f"{node} {node_card[node]}")

    for (left, right) in edges:
        lines.append(f"{left} {right}")

    return "\n".join(lines)