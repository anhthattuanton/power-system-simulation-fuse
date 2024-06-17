"""
Tests for assignment 1
"""

import pytest

from power_system_simulation.graph_processing import (
    GraphCycleError,
    GraphNotFullyConnectedError,
    GraphProcessor,
    IDNotFoundError,
    IDNotUniqueError,
    InputLengthDoesNotMatchError,
)

def test_2_ID_not_unique():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 2]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotUniqueError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Vertex IDs contains ID also in edge IDs."

def test_vertex_ID_not_unique():
    vertex_ids = [0, 2, 2]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotUniqueError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Vertex IDs contains duplicated IDs."

def test_edge_ID_not_unique():
    vertex_ids = [0, 2, 4]
    edge_ids = [3, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotUniqueError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Edge IDs contains duplicated IDs."

def test_input_length_error():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3, 5]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(InputLengthDoesNotMatchError)as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Edge IDs length not equals to vertex ID pairs length."

def test_edge_id_pairs():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 3)]
    edge_enabled = [True, True]
    source_id = 0
    with pytest.raises(IDNotFoundError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Vertex ID pairs contains invalid ID."


def test_edge_enabled():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True, False]
    source_id = 0
    with pytest.raises(InputLengthDoesNotMatchError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Edge ID length not equal to edge status length."


def test_source_vertex():
    vertex_ids = [0, 2, 4]
    edge_ids = [1, 3]
    edge_vertex_id = [(0, 2), (2, 4)]
    edge_enabled = [True, True]
    source_id = 5
    with pytest.raises(IDNotFoundError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Source ID should be a valid vertex ID."

def test_graph_fully_connected():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, False, False, True, False, True]
    source_id = 0
    with pytest.raises(GraphNotFullyConnectedError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Grid should be fully connected."

def test_graph_cycles():
    vertex_ids = [0, 2, 4, 6, 10]
    edge_ids = [1, 3, 5, 7, 8, 9]
    edge_vertex_id = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
    edge_enabled = [True, True, True, True, False, True]
    source_id = 0
    with pytest.raises(GraphCycleError) as error:
        result = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_vertex_id,
            edge_enabled=edge_enabled,
            source_vertex_id=source_id,
        )
    assert str(error.value) == "Grid should be acyclic."
    
