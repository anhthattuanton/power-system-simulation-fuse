"""
Tests for assignment 1
"""

import pytest

from power_system_simulation.graph_processing import (
    EdgeAlreadyDisabledError,
    GraphCycleError,
    GraphNotFullyConnectedError,
    GraphProcessor,
    IDNotFoundError,
    IDNotUniqueError,
    InputLengthDoesNotMatchError,
)


def test_graph_fully_connected():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, False, False, True, False, True]
    source_id = 0
    with pytest.raises(GraphNotFullyConnectedError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_ID_not_unique():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 2]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotUniqueError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_duplicated_ID():
    vertex_ids = [0, 2, 2]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotUniqueError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_input_length_error():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3, 5]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_edge_id_pairs():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 3)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotFoundError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_edge_enabled():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True, False]
    source_id = 0
    with pytest.raises(InputLengthDoesNotMatchError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_source_vertex():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 5
    with pytest.raises(IDNotFoundError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )


def test_graph_cycles():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, True, True, True, False, True]
    source_id = 0
    with pytest.raises(GraphCycleError):
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
