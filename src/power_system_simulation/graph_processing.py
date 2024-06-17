"""
This is a skeleton for the graph processing assignment.

We define a graph processor class with some function skeletons.
"""

# setup:
from typing import List, Tuple

import networkx as nx


class IDNotFoundError(Exception):
    """
    id not found
    """

    def __init__(self, error: str) -> None:
        self.error = error


class InputLengthDoesNotMatchError(Exception):
    """
    length of edges related variable must be the same
    """

    def __init__(self, error: str) -> None:
        self.error = error


class IDNotUniqueError(Exception):
    """
    all id must be unique
    """

    def __init__(self, error: str) -> None:
        self.error = error


class GraphNotFullyConnectedError(Exception):
    """
    graph must be fully connected
    """

    def __init__(self, error: str) -> None:
        self.error = error


class GraphCycleError(Exception):
    """
    graph must not contain any cycle
    """

    def __init__(self, error: str) -> None:
        self.error = error


class EdgeAlreadyDisabledError(Exception):
    """
    related edge has already been disabled
    """

    def __init__(self, error: str) -> None:
        self.error = error


class GraphProcessor:
    """
    General documentation of this class.
    You need to describe the purpose of this class and the functions in it.
    We are using an undirected graph in the processor.
    """

    def __init__(
        self,
        edge_ids: List[int],
        edge_vertex_id_pairs: List[Tuple[int, int]],
        edge_enabled: List[bool],
        source_vertex_id: int,
    ) -> None:

        # put your implementation here
        # 1. vertex_ids and edge_ids should be unique.
        vertex_ids = {node for pairs in edge_vertex_id_pairs for node in pairs}
        # if len(set(vertex_ids)) != len(vertex_ids):
        #     raise IDNotUniqueError("Vertex IDs contains duplicated IDs.")
        if len(set(edge_ids)) != len(edge_ids):
            raise IDNotUniqueError("Edge IDs contains duplicated IDs.")
        for n in vertex_ids:
            if n in edge_ids:
                raise IDNotUniqueError("Vertex IDs contains ID also in edge IDs.")
        # 2. edge_vertex_id_pairs should have the same length as edge_ids.
        if len(edge_vertex_id_pairs) != len(edge_ids):
            error = "Edge IDs length not equals to vertex ID pairs length."
            raise InputLengthDoesNotMatchError(error)
        # 4. edge_enabled should have the same length as edge_ids.
        if len(edge_enabled) != len(edge_ids):
            raise InputLengthDoesNotMatchError("Edge ID length not equal to edge status length.")
        # 5. source_vertex_id should be a valid vertex id.
        if source_vertex_id not in vertex_ids:
            raise IDNotFoundError("Source ID should be a valid vertex ID.")
        # 6. The graph should be fully connected. (GraphNotFullyConnectedError)
        enabled_edge_ids = [id for id, is_true in zip(edge_ids, edge_enabled) if is_true]
        enabled_pairs = [id for id, is_true in zip(edge_vertex_id_pairs, edge_enabled) if is_true]
        # enabled_vertex_ids = {id for edge in enabled_pairs for id in edge}
        network = nx.Graph()
        network.add_nodes_from(vertex_ids)
        network.add_edges_from(enabled_pairs)
        if not nx.is_connected(G=network):
            raise GraphNotFullyConnectedError("Grid should be fully connected.")
        # 7. The graph should not contain cycles. (GraphCycleError)
        # if len(enabled_vertex_ids) - 1 != len(enabled_edge_ids):
        if nx.cycle_basis(network):
            raise GraphCycleError("Grid should be acyclic.")
        self.vertex_ids = vertex_ids
        self.edge_ids = edge_ids
        self.edge_vertex_id_pairs = edge_vertex_id_pairs
        self.source_vertex_id = source_vertex_id
        self.enabled_edge_ids = enabled_edge_ids
        self.enabled_pairs = enabled_pairs
        self.network = network

    def find_downstream_vertices(self, edge_id: int) -> List[int]:
        """
        Find downstream vertices by using dfs on 2 vertices
        from the corresponding edge
        """
        if edge_id not in self.edge_ids:
            raise IDNotFoundError("Invalid edge ID.")
        if edge_id not in self.enabled_edge_ids:
            return []
        index = self.edge_ids.index(edge_id)
        vertex_ids = self.edge_vertex_id_pairs[index]
        self.network.remove_edge(*vertex_ids)
        downstream_vertices = []
        for vertex_id in vertex_ids:
            output = list(nx.dfs_preorder_nodes(self.network, source=vertex_id))
            if self.source_vertex_id not in output:
                downstream_vertices = output
                break
        # recovering the graph:
        self.network.add_edge(*vertex_ids)
        return downstream_vertices

    def find_alternative_edges(self, disabled_edge_id: int) -> List[int]:
        """
        Find alternative edges by continously enabling each disabled edge
        and checking if the grid becomes connected.
        """
        # put your implementation here
        if disabled_edge_id not in self.edge_ids:
            raise IDNotFoundError("Invalid edge ID.")
        if disabled_edge_id not in self.enabled_edge_ids:
            raise EdgeAlreadyDisabledError("Edge is already disabled.")
        # get data related to disabled_edge_id
        index = self.edge_ids.index(disabled_edge_id)
        vertex_ids = self.edge_vertex_id_pairs[index]
        self.enabled_pairs.remove(vertex_ids)
        self.network.remove_edge(*vertex_ids)
        alternative_edges = []
        for vertices_pair in self.edge_vertex_id_pairs:
            if vertices_pair not in self.enabled_pairs:
                self.network.add_edge(*vertices_pair)
                if not nx.cycle_basis(self.network) and nx.is_connected(self.network):
                    edge_index = self.edge_vertex_id_pairs.index(vertices_pair)
                    alternative_edges.append(self.edge_ids[edge_index])
                self.network.remove_edge(*vertices_pair)
        # recovering the network
        self.enabled_pairs.append(vertex_ids)
        self.network.add_edge(*vertex_ids)
        if disabled_edge_id in alternative_edges:
            alternative_edges.remove(disabled_edge_id)
        return alternative_edges
