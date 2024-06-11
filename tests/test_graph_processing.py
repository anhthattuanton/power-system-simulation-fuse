import pytest
from power_system_simulation.graph_processing import GraphProcessor, IDNotFoundError, InputLengthDoesNotMatchError, IDNotUniqueError, GraphNotFullyConnectedError, GraphCycleError, EdgeAlreadyDisabledError

def test_graph_processor_initialization():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert gp.vertex_ids == vertex_ids
    assert gp.edge_ids == edge_ids
    assert gp.edge_vertex_id_pairs == edge_vertex_id_pairs
    assert gp.edge_enabled == edge_enabled
    assert gp.source_vertex_id == source_vertex_id

def test_graph_processor_id_not_unique_error():
    with pytest.raises(IDNotUniqueError):
        GraphProcessor([0, 1, 1], [1, 2, 3], [(0, 1), (1, 2), (2, 3)], [True, True, True], 0)

def test_graph_processor_input_length_does_not_match_error():
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2)], [True, True, True], 0)

def test_graph_processor_id_not_found_error():
    with pytest.raises(IDNotFoundError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2), (2, 4)], [True, True, True], 0)

def test_graph_processor_graph_not_fully_connected_error():
    with pytest.raises(GraphNotFullyConnectedError):
        GraphProcessor([0, 1, 2, 3], [1, 2, 3], [(0, 1), (2, 3), (3, 2)], [True, True, True], 0)

def test_graph_processor_graph_cycle_error():
    with pytest.raises(GraphCycleError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2), (2, 0)], [True, True, True], 0)

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
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphNotFullyConnectedError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphNotFullyConnectedError"

def test_find_alternative_edges():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, False, False]
    source_vertex_id = 0
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphCycleError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphCycleError"

def test_find_alternative_edges_no_alternative():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, True, True]
    source_vertex_id = 0
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphCycleError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphCycleError"

def test_invalid_vertex_in_edge_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 4), (2, 3)]  # 4 is invalid
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotFoundError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_invalid_source_vertex():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 4  # Invalid source vertex
    with pytest.raises(IDNotFoundError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_vertex_ids():
    vertex_ids = [0, 1, 1, 3]  # Non-unique vertex ID
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_edge_ids():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 2]  # Non-unique edge ID
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_id_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2)]  # Mismatched length
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_enabled():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True]  # Mismatched length
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_graph_without_cycles():
    vertex_ids = [0, 1, 2, 3, 4]
    edge_ids = [1, 2, 3, 4]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4)]
    edge_enabled = [True, True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert set(gp.find_downstream_vertices(1)) == {2, 3, 4}
from power_system_simulation.graph_processing import GraphProcessor, IDNotFoundError, InputLengthDoesNotMatchError, IDNotUniqueError, GraphNotFullyConnectedError, GraphCycleError, EdgeAlreadyDisabledError

def test_graph_processor_initialization():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert gp.vertex_ids == vertex_ids
    assert gp.edge_ids == edge_ids
    assert gp.edge_vertex_id_pairs == edge_vertex_id_pairs
    assert gp.edge_enabled == edge_enabled
    assert gp.source_vertex_id == source_vertex_id

def test_graph_processor_id_not_unique_error():
    with pytest.raises(IDNotUniqueError):
        GraphProcessor([0, 1, 1], [1, 2, 3], [(0, 1), (1, 2), (2, 3)], [True, True, True], 0)

def test_graph_processor_input_length_does_not_match_error():
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2)], [True, True, True], 0)

def test_graph_processor_id_not_found_error():
    with pytest.raises(IDNotFoundError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2), (2, 4)], [True, True, True], 0)

def test_graph_processor_graph_not_fully_connected_error():
    with pytest.raises(GraphNotFullyConnectedError):
        GraphProcessor([0, 1, 2, 3], [1, 2, 3], [(0, 1), (2, 3), (3, 2)], [True, True, True], 0)

def test_graph_processor_graph_cycle_error():
    with pytest.raises(GraphCycleError):
        GraphProcessor([0, 1, 2], [1, 2, 3], [(0, 1), (1, 2), (2, 0)], [True, True, True], 0)

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
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphNotFullyConnectedError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphNotFullyConnectedError"

def test_find_alternative_edges():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, False, False]
    source_vertex_id = 0
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphCycleError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphCycleError"

def test_find_alternative_edges_no_alternative():
    vertex_ids = [0, 1, 2, 3, 4, 5]
    edge_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4), (2, 5)]
    edge_enabled = [True, True, True, True, True, True, True, True]
    source_vertex_id = 0
    try:
        gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    except GraphCycleError:
        assert True  # This is expected
    else:
        assert False, "Expected GraphCycleError"

def test_invalid_vertex_in_edge_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 4), (2, 3)]  # 4 is invalid
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotFoundError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_invalid_source_vertex():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 4  # Invalid source vertex
    with pytest.raises(IDNotFoundError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_vertex_ids():
    vertex_ids = [0, 1, 1, 3]  # Non-unique vertex ID
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_non_unique_edge_ids():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 2]  # Non-unique edge ID
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_id_pairs():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2)]  # Mismatched length
    edge_enabled = [True, True, True]
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_mismatched_length_edge_enabled():
    vertex_ids = [0, 1, 2, 3]
    edge_ids = [1, 2, 3]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3)]
    edge_enabled = [True, True]  # Mismatched length
    source_vertex_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

def test_graph_without_cycles():
    vertex_ids = [0, 1, 2, 3, 4]
    edge_ids = [1, 2, 3, 4]
    edge_vertex_id_pairs = [(0, 1), (1, 2), (2, 3), (3, 4)]
    edge_enabled = [True, True, True, True]
    source_vertex_id = 0
    gp = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)
    assert set(gp.find_downstream_vertices(1)) == {2, 3, 4}