
from power_system_simulation.graph_processing import GraphProcessor
from power_system_simulation.power_grid_model_ass2 import powerGridModelling,dataConversion

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import json
import networkx as nx
import random
from math import floor

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
        for id in feeder_ids:
            if id not in dataset["line"]["id"].tolist():
                raise IDNotFoundError
        # if not set(feeder_ids).issubset(set(dataset["line"]["id"])):
        #     raise IDNotFoundError
        for id in feeder_ids:
            idx.append(np.asarray(dataset["line"]["id"] == id).nonzero()[0].item())
        for index in idx:
            if dataset["line"]["from_node"][index] not in dataset["transformer"]["to_node"]:
                print(idx)
                raise InvalidFeederError
            
        vertex_ids = [id for id in dataset["node"]["id"]] + dataset["source"]["id"].tolist()
        
        edge_ids = [id for id in dataset["line"]["id"]] 
        edge_vertex_id_pairs = [id for id in zip(dataset["line"]["from_node"], 
                                    dataset["line"]["to_node"])]
        edge_enabled = (dataset["line"]["to_status"] != [0])
        source_vertex_id = dataset["source"]["id"]
        grid = GraphProcessor(vertex_ids= vertex_ids,
                       edge_ids= edge_ids, 
                       edge_vertex_id_pairs= edge_vertex_id_pairs, 
                       edge_enabled= edge_enabled, 
                       source_vertex_id= source_vertex_id)
        if list(ev_pool.index) != list(active_load_profile.index):
            raise InvalidProfilesError
        if active_load_profile.columns.to_list() != reactive_load_profile.columns.to_list():
            raise InvalidProfilesError
        if not set(active_load_profile.columns).issubset(set(dataset["sym_load"]["id"])):
            raise InvalidProfilesError
        # The number of EV charging profile is at least the same as the number of sym_load.
        if len(ev_pool.columns.to_list()) < len(list(dataset["sym_load"]["id"])):
            raise InvalidProfilesError
        model = PowerGridModel(dataset)
        self.input_data = dataset
        self.model = model
        self.grid = grid
        self.feeder_ids = feeder_ids
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        self.ev_pool = ev_pool

    def EV_penetration_level(self, penetration_level: int):
        nr_of_EV = floor(penetration_level * len(self.input_data["sym_load"]["id"]) / len(self.feeder_ids))
        EV_ids = []
        for n in self.feeder_ids:
            nodes_feeder = self.grid.find_downstream_vertices(n)
            loads_feeder = []
            for m in nodes_feeder:
                if m in self.input_data["sym_load"]["node"]:
                    load_idx = np.where(self.input_data["sym_load"]["node"] == m)
                    loads_feeder.extend(list(self.input_data["sym_load"]["id"][load_idx]))
            EV_ids.extend(random.sample(loads_feeder, nr_of_EV))
        ev_profiles = random.sample(list(self.ev_pool.columns), len(EV_ids))
        for idx, val in enumerate(ev_profiles):
            ev_prof = self.ev_pool.iloc[:, ev_profiles[idx]].tolist()
            self.active_load_profile[EV_ids[idx]] = self.active_load_profile[EV_ids[idx]] + ev_prof
        df_result_u_pu, df_result_loading_pu = powerGridModelling(dataset= self.input_data,
                                                                  active_load_profile= self.active_load_profile,
                                                                  reactive_load_profile= self.reactive_load_profile) 
        return df_result_u_pu, df_result_loading_pu

        
