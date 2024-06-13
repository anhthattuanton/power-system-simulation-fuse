"""
This is a skeleton for the graph processing assignment.

We define a graph processor class with some function skeletons.
"""
from typing import List, Tuple
import networkx as nx

class IDNotFoundError(Exception):
    pass

class InputLengthDoesNotMatchError(Exception):
    pass

class IDNotUniqueError(Exception):
    pass

class GraphNotFullyConnectedError(Exception):
    pass

class GraphCycleError(Exception):
    pass

class EdgeAlreadyDisabledError(Exception):
    pass

class GraphProcessor:
    """
    General documentation of this class.
    You need to describe the purpose of this class and the functions in it.
    We are using an undirected graph in the processor.
    """
    def __init__(
        self,
        vertex_ids: List[int],
        edge_ids: List[int],
        edge_vertex_id_pairs: List[Tuple[int, int]],
        edge_enabled: List[bool],
        source_vertex_id: int,
        validate_connected: bool = True
    ) -> None:
        """
        Initialize a graph processor object with an undirected graph.
        Only the edges which are enabled are taken into account.
        Check if the input is valid and raise exceptions if not.
        The following conditions should be checked:
            1. vertex_ids and edge_ids should be unique. (IDNotUniqueError)
            2. edge_vertex_id_pairs should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            3. edge_vertex_id_pairs should contain valid vertex ids. (IDNotFoundError)
            4. edge_enabled should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            5. source_vertex_id should be a valid vertex id. (IDNotFoundError)
            6. The graph should be fully connected. (GraphNotFullyConnectedError)
            7. The graph should not contain cycles. (GraphCycleError)
        If one certain condition is not satisfied, the error in the parentheses should be raised.

        Args:
            vertex_ids: list of vertex ids
            edge_ids: list of edge ids
            edge_vertex_id_pairs: list of tuples of two integer
                Each tuple is a vertex id pair of the edge.
            edge_enabled: list of bools indicating if an edge is enabled or not
            source_vertex_id: vertex id of the source in the graph
        """
        # 1. vertex_ids and edge_ids should be unique. (IDNotUniqueError)
        if len(set(vertex_ids)) != len(vertex_ids) or len(set(edge_ids)) != len(edge_ids):
            raise IDNotUniqueError("Vertex IDs or Edge IDs are not unique.")
        # 2. edge_vertex_id_pairs should have the same length as edge_ids. (InputLengthDoesNotMatchError)
        if len(edge_vertex_id_pairs) != len(edge_ids):
            raise InputLengthDoesNotMatchError("Edge ID pairs length does not match edge IDs length.")
        # 3. edge_vertex_id_pairs should contain valid vertex ids. (IDNotFoundError)
        for x, y in edge_vertex_id_pairs:
            if x not in vertex_ids or y not in vertex_ids:
                raise IDNotFoundError("One or more vertex IDs in edge_vertex_id_pairs are invalid.")
        # 4. edge_enabled should have the same length as edge_ids. (InputLengthDoesNotMatchError)
        if len(edge_enabled) != len(edge_ids):
            raise InputLengthDoesNotMatchError("edge_enabled length does not match edge IDs length.")
        # 5. source_vertex_id should be a valid vertex id. (IDNotFoundError)
        if source_vertex_id not in vertex_ids:
            raise IDNotFoundError("Source vertex ID is invalid.")

        self.vertex_ids = vertex_ids
        self.edge_ids = edge_ids
        self.edge_vertex_id_pairs = edge_vertex_id_pairs
        self.edge_enabled = edge_enabled
        self.source_vertex_id = source_vertex_id

        self.graph = nx.Graph()
        for (x, y), enabled in zip(edge_vertex_id_pairs, edge_enabled):
            if enabled:
                self.graph.add_edge(x, y)

        if validate_connected:
            self.validate_graph()

    def validate_graph(self):
        enabled_graph = nx.Graph()
        enabled_graph.add_nodes_from(self.vertex_ids)
        for edge, enabled in zip(self.edge_vertex_id_pairs, self.edge_enabled):
            if enabled:
                enabled_graph.add_edge(*edge)

        if len(enabled_graph.edges) > 0 and not nx.is_connected(enabled_graph):
            raise GraphNotFullyConnectedError("The graph is not fully connected based on enabled edges.")

        try:
            cycles = list(nx.find_cycle(enabled_graph, orientation='ignore'))
            if cycles:
                raise GraphCycleError("The graph contains cycles based on enabled edges.")
        except nx.exception.NetworkXNoCycle:
            pass

    def find_downstream_vertices(self, edge_id: int) -> List[int]:
        """
        Given an edge id, return all the vertices which are in the downstream of the edge,
            with respect to the source vertex.
            Including the downstream vertex of the edge itself!

        Only enabled edges should be taken into account in the analysis.
        If the given edge_id is a disabled edge, it should return empty list.
        If the given edge_id does not exist, it should raise IDNotFoundError.


        For example, given the following graph (all edges enabled):

            vertex_0 (source) --edge_1-- vertex_2 --edge_3-- vertex_4

        Call find_downstream_vertices with edge_id=1 will return [2, 4]
        Call find_downstream_vertices with edge_id=3 will return [4]

        Args:
            edge_id: edge id to be searched

        Returns:
            A list of all downstream vertices.
        """
        if edge_id not in self.edge_ids:
            raise IDNotFoundError("Edge ID not found")
        index = self.edge_ids.index(edge_id)
        if not self.edge_enabled[index]:
            return []

        vertex_ids = self.edge_vertex_id_pairs[index]

        # Temporarily disable the edge and find the connected component
        self.graph.remove_edge(*vertex_ids)

        downstream_vertices = []
        for vertex_id in vertex_ids:
            if not nx.has_path(self.graph, self.source_vertex_id, vertex_id):
                downstream_vertices = list(nx.dfs_postorder_nodes(self.graph, source=vertex_id))
                break

        self.graph.add_edge(*vertex_ids)

        return [v for v in downstream_vertices if v != vertex_ids[0] and v != vertex_ids[1]]

    def find_alternative_edges(self, disabled_edge_id: int) -> List[int]:
        """
        Given an enabled edge, do the following analysis:
            If the edge is going to be disabled,
                which (currently disabled) edge can be enabled to ensure
                that the graph is again fully connected and acyclic?
            Return a list of all alternative edges.
        If the disabled_edge_id is not a valid edge id, it should raise IDNotFoundError.
        If the disabled_edge_id is already disabled, it should raise EdgeAlreadyDisabledError.
        If there are no alternative to make the graph fully connected again, it should return empty list.


        For example, given the following graph:

        vertex_0 (source) --edge_1(enabled)-- vertex_2 --edge_9(enabled)-- vertex_10
                 |                               |
                 |                           edge_7(disabled)
                 |                               |
                 -----------edge_3(enabled)-- vertex_4
                 |                               |
                 |                           edge_8(disabled)
                 |                               |
                 -----------edge_5(enabled)-- vertex_6

        Call find_alternative_edges with disabled_edge_id=1 will return [7]
        Call find_alternative_edges with disabled_edge_id=3 will return [7, 8]
        Call find_alternative_edges with disabled_edge_id=5 will return [8]
        Call find_alternative_edges with disabled_edge_id=9 will return []

        Args:
            disabled_edge_id: edge id (which is currently enabled) to be disabled

        Returns:
            A list of alternative edge ids.
        """
        if disabled_edge_id not in self.edge_ids:
            raise IDNotFoundError("Edge ID not found")
        if not self.edge_enabled[self.edge_ids.index(disabled_edge_id)]:
            raise EdgeAlreadyDisabledError("Edge is already disabled")

        index = self.edge_ids.index(disabled_edge_id)
        vertex_ids = self.edge_vertex_id_pairs[index]

        self.graph.remove_edge(*vertex_ids)
        alternative_edges = []
        for (u, v), eid, enabled in zip(self.edge_vertex_id_pairs, self.edge_ids, self.edge_enabled):
            if not enabled:
                self.graph.add_edge(u, v)
                try:
                    if nx.is_connected(self.graph) and not list(nx.find_cycle(self.graph, orientation='ignore')):
                        alternative_edges.append(eid)
                except nx.exception.NetworkXNoCycle:
                    alternative_edges.append(eid)
                self.graph.remove_edge(u, v)
        self.graph.add_edge(*vertex_ids)

        return alternative_edges if alternative_edges else []
