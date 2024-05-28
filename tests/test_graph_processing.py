from power_system_simulation.graph_processing import __init__, find_downstream_vertices, find_alternative_edges

def test_find_alternative_edges():
    __init__([0,1,2,3,4],[1,2,3,4,5,6],[[0,1],[0,2],[0,3],[1,2],[2,3],[2,4]],[1,1,1,0,1],0)
    print(find_alternative_edges(2))
