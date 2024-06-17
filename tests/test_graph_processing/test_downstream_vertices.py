import pytest

from power_system_simulation.graph_processing import GraphProcessor, IDNotFoundError


def test_downstream_vertices():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    network = GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id,
        edge_enabled=edge_enabled,
        source_vertex_id=source_id,
    )
    assert network.find_downstream_vertices(edge_id=1) == [2, 4]


def test_id_not_found_downstream():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, True, True, False, False, True]
    source_id = 0
    data = GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id,
        edge_enabled=edge_enabled,
        source_vertex_id=source_id,
    )
    with pytest.raises(IDNotFoundError) as error:
        data.find_downstream_vertices(edge_id=2)
    assert str(error.value) == "Invalid edge ID."


def test_edge_already_disabled_downstream():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, True, True, False, False, True]
    source_id = 0
    data = GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id,
        edge_enabled=edge_enabled,
        source_vertex_id=source_id,
    )
    assert data.find_downstream_vertices(edge_id=7) == []
