import pytest

from power_system_simulation.graph_processing import EdgeAlreadyDisabledError, GraphProcessor, IDNotFoundError


def test_alternativeEdges():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, True, True, False, False, True]
    source_id = 0
    network = GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id,
        edge_enabled=edge_enabled,
        source_vertex_id=source_id,
    )
    assert network.find_alternative_edges(disabled_edge_id=3) == [7, 8]


def test_id_not_found():
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
        data.find_alternative_edges(disabled_edge_id=11)
    assert str(error.value) == "Invalid edge ID."


def test_edge_already_disabled():
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
    with pytest.raises(EdgeAlreadyDisabledError) as error:
        data.find_alternative_edges(disabled_edge_id=7)
    assert str(error.value) == "Edge is already disabled."


def test_no_possible_solution():
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
    assert data.find_alternative_edges(disabled_edge_id=9) == []
