import pytest
from power_system_simulation.graph_processing import (
    GraphProcessor, GraphNotFullyConnectedError, GraphCycleError, IDNotFoundError, EdgeAlreadyDisabledError, InputLengthDoesNotMatchError, IDNotUniqueError
)

def test_find_downstream_vertices():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert set(gp.find_downstream_vertices(1)) == {2, 3}

def test_find_downstream_vertices_disabled_edge():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, False, True]
    source_vertex_id = 0
    with pytest.raises(GraphNotFullyConnectedError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_find_alternative_edges():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, False, False]
    source_vertex_id = 0
    with pytest.raises(GraphCycleError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_find_alternative_edges_no_alternative():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, True, True]
    source_vertex_id = 0
    with pytest.raises(GraphCycleError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_graph_without_cycles():
    vertex_ids = [0, 1, 2, 3, 4]
    edge_ids = [1, 2, 3, 4]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4)]
    edge_enabled = [True, True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert set(gp.find_downstream_vertices(1)) == {2, 3, 4}

def test_find_downstream_vertices_edge_not_found():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    with pytest.raises(IDNotFoundError):
        gp.find_downstream_vertices(4)

def test_find_alternative_edges_edge_not_found():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    with pytest.raises(IDNotFoundError):
        gp.find_alternative_edges(4)

def test_find_alternative_edges_already_disabled():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, False, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id, validate_connected=False)
    with pytest.raises(EdgeAlreadyDisabledError):
        gp.find_alternative_edges(2)

def test_find_alternative_edges_no_cycle():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3, 4]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]
    edge_enabled = [True, True, True, True]
    source_vertex_id = 0
    with pytest.raises(GraphCycleError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_unique_vertex_edge_ids():
    vertex_ids = [0, 1, 2, 2]  # Duplicate vertex ID
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_input_length_mismatch():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2)]  # Length mismatch
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_invalid_vertex_in_edge_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 4), (2, 3)]  # 4 is invalid
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotFoundError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_invalid_source_vertex():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 4  # Invalid source vertex
    with pytest.raises(IDNotFoundError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_vertex_ids():
    vertex_ids = [0, 1, 1, 3]  # Non-unique vertex ID
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_edge_ids():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 2]  # Non-unique edge ID
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_id_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2)]  # Mismatched length
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_enabled():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True]  # Mismatched length
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_find_downstream_vertices_all_disabled_edges():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [False, False, False]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert gp.find_downstream_vertices(1) == []

def test_graph_not_fully_connected():
    vertex_ids = [0, 1, 2, 3, 4]
    edge_ids = [1, 2, 3, 4]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4)]
    edge_enabled = [True, True, True, False]
    source_vertex_id = 0
    with pytest.raises(GraphNotFullyConnectedError):
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_alternative_edges_when_disabled():
    vertex_ids = [0, 1, 2, 3, 4]
    edge_ids = [1, 2, 3, 4, 5]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    edge_enabled = [True, True, True, True, False]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id, validate_connected=False)
    alternative_edges = gp.find_alternative_edges(4)
    assert alternative_edges == [5]
