from power_system_simulation.graph_processing import GraphProcessor
from power_system_simulation.power_grid_model import powerGridModelling,dataConversion

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import json
import networkx as nx

from power_grid_model import (
    LoadGenType,
    PowerGridModel,
    CalculationType,
    CalculationMethod,
    MeasuredTerminalType,
    initialize_array
)

from power_grid_model.validation import (
    assert_valid_input_data,
    assert_valid_batch_data
)

class InvalidNumberOfSourceError(Exception):
    pass

class InvalidNumberOfTransformerError(Exception):
    pass

class IDNotFoundError(Exception):
    pass

class IDNotUniqueError(Exception):
    pass

class InvalidFeederError(Exception):
    pass

class InvalidProfilesError(Exception):
    pass

class GridAnalysis:
    def __init__(
            self,
            data_path: str,
            feeder_ids: list[int],
            active_load_profile_path: str,
            reactive_load_profile_path: str,
            ev_pool_path: str
    ) -> None:
        dataset, active_load_profile, reactive_load_profile = dataConversion(data_path=data_path, 
                                                                             active_sym_load_path= active_load_profile_path, 
                                                                             reactive_sym_load_path= reactive_load_profile_path)
        ev_pool = pd.read_parquet(ev_pool_path)
        idx = []
        if len(dataset["source"]) != 1:
            raise InvalidNumberOfSourceError
        if len(dataset["transformer"]) != 1:
            raise InvalidNumberOfTransformerError
        if len(set(feeder_ids)) != len(feeder_ids):
            raise IDNotUniqueError
        if not set(feeder_ids).issubset(set(dataset["line"]["id"])):
            raise IDNotFoundError
        for id in feeder_ids:
            idx.append(np.asarray(dataset["line"]["id"] == id).nonzero())
        for index in idx:
            if dataset["line"]["from_node"][index] not in dataset["transformer"]["to_node"]:
                raise InvalidFeederError
        """
        Make use of the GraphProcessor to check if grid is fully connected and acyclic.
        Could be faster if we have more time because GraphProcessor will validates the
        data again, which is done already by dataConversion function already.
        """

        vertex_ids = [id for id in dataset["node"]["id"]]
        edge_ids = [id for id in dataset["line"]["id"]]
        edge_vertex_id_pairs = [zip(dataset["line"]["from_node"], 
                                    dataset["line"]["to_node"])]
        edge_enabled = [dataset["line"]["to_status"] != 0]
        sourve_vertex_id = dataset["source"]["id"]
        grid = GraphProcessor(vertex_ids= vertex_ids, 
                       edge_ids= edge_ids, 
                       edge_vertex_id_pairs= edge_vertex_id_pairs, 
                       edge_enabled= edge_enabled, 
                       source_vertex_id= sourve_vertex_id)
        if ev_pool.index != active_load_profile.index:
            raise InvalidProfilesError
        if active_load_profile.columns.to_list() != reactive_load_profile.columns.to_list():
            raise InvalidProfilesError
        if not set(active_load_profile.columns).issubset(set(dataset["sym_load"]["id"])):
            raise InvalidProfilesError
        
        model = PowerGridModel(dataset)
        
        
