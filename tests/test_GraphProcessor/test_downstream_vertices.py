from power_system_simulation.graph_processing import GraphProcessor

def test_graphProcessor():
    vertex_ids = [0,2,4]
    edge_ids = [1,3]
    edge_vertex_id = [(0,2),(2,4)]
    edge_enabled = [True,True]
    source_id = 0
    network = GraphProcessor(vertex_ids= vertex_ids, edge_ids= edge_ids, edge_vertex_id_pairs= edge_vertex_id, edge_enabled= edge_enabled, source_vertex_id= source_id)
    assert network.find_downstream_vertices(edge_id= 1) == [2,4]