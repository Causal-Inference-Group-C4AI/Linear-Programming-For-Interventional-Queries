import networkx as nx
from typing import Optional
from pandas import DataFrame

from causal_usp_icti.utils.funcoes import get_tuple_edges
from causal_usp_icti.graph.graph import Graph
from causal_usp_icti.utils.parser import parse_edges, parse_state, parse_target

class CausalModel:
    def __init__(
        self, 
        data: DataFrame,
        edges: str,
        unobservables: list[str] | str | None = [],
        interventions: list[str] | str | None = [],
        target: str | None = ""
    ) -> None:
            self._data = data
            self.graph = input_processor()
            self.unobservables = parse_state(unobservables)
            self.interventions = parse_state(interventions)
            self.target = parse_state(target)

    def visualize_graph(self):
        '''
            Create an image and plot the DAG
        '''
        # TODO: Implement in the class Graph
        raise NotImplementedError

    def _update_list(self, attr_name: str, values: list[str], reset: bool = False) -> None:
        attr = getattr(self, attr_name)
        if reset:
            attr.clear()
        if self.is_nodes_in_graph(values):
            attr.extend(values)
            return
        raise Exception(f"Nodes '{values}' not present in the defined graph.")
    
    def add_interventions(self, interventions: list[str]) -> None:
        self._update_list("interventions", interventions)

    def set_interventions(self, interventions: list[str]) -> None:
        self._update_list("interventions", interventions, reset=True)
    
    def add_unobservables(self, unobservables):
        self._update_list("unobservables", unobservables)

    def set_unobservables(self, unobservables):
        self._update_list("unobservables", unobservables, reset=True)

    def set_target(self, target: str) -> None:
        self.target.clear()
        if self.is_nodes_in_graph([target]):
            self.target = target
            return
        raise Exception(f"Nodes '{target}' not present in the defined graph.")

    def is_nodes_in_graph(self, nodes: list[str]):
        for node in nodes:
            if node not in self.graph:
                return False
        return True





def parse_str_to_nx_graph(edges_str: str, latents: list[str]) -> str:
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
