from power_system_simulation.graph_processing import GraphProcessor
from power_system_simulation.power_grid_modelling import PowerGridModelling


import numpy as np
import pandas as pd
import random
from math import floor
from typing import Dict

from power_grid_model import (
    LoadGenType,
    PowerGridModel,
    CalculationType,
    CalculationMethod,
    MeasuredTerminalType,
    initialize_array
)

from power_grid_model.utils import (
    json_deserialize_from_file, 
    json_serialize
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

class FeederIDNotUniqueError(Exception):
    pass

class InvalidFeederError(Exception):
    pass

class InvalidProfilesError(Exception):
    pass

class LineNotFullyConnectedError(Exception):
    pass

class GridAnalysis:
    def __init__(
            self,
            data_path: str | Dict[str, np.ndarray | Dict[str, np.ndarray]],
            feeder_ids: list[int],
            active_load_profile_path: str | pd.DataFrame,
            reactive_load_profile_path: str | pd.DataFrame,
            ev_pool_path: str | pd.DataFrame
    ) -> None:
        if type(data_path) == str:
            dataset = json_deserialize_from_file(data_path)
            assert_valid_input_data(input_data= dataset,
                                    calculation_type= CalculationType.power_flow)
        else:
            dataset = data_path
        if type(active_load_profile_path) ==  str:
            active_load_profile = pd.read_parquet(active_load_profile_path)
        else:
            active_load_profile = active_load_profile_path
        if type(reactive_load_profile_path) == str:
            reactive_load_profile = pd.read_parquet(reactive_load_profile_path)
        else:
            reactive_load_profile = reactive_load_profile_path
        if active_load_profile.index.to_list() != reactive_load_profile.index.to_list():
            raise InvalidProfilesError
        load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
        load_profile["id"] = active_load_profile.columns.to_numpy()
        load_profile["p_specified"] = active_load_profile.to_numpy()
        load_profile["q_specified"] = reactive_load_profile.to_numpy()
        update_dataset = {"sym_load": load_profile}
        assert_valid_batch_data(input_data= dataset, 
                            update_data= update_dataset, 
                            calculation_type= CalculationType.power_flow)
        if type(ev_pool_path) == str:
            ev_pool = pd.read_parquet(ev_pool_path)
        else:
            ev_pool = ev_pool_path
        idx = []
        if len(dataset["source"]) != 1:
            raise InvalidNumberOfSourceError
        if len(dataset["transformer"]) != 1:
            raise InvalidNumberOfTransformerError
        if len(set(feeder_ids)) != len(feeder_ids):
            raise FeederIDNotUniqueError
        for id in feeder_ids:
            if id not in dataset["line"]["id"].tolist():
                raise InvalidFeederError
        # if not set(feeder_ids).issubset(set(dataset["line"]["id"])):
        #     raise IDNotFoundError
        for id in feeder_ids:
            idx.append(np.asarray(dataset["line"]["id"] == id).nonzero()[0].item())
        for index in idx:
            if dataset["line"]["from_node"][index] not in dataset["transformer"]["to_node"]:
                print(idx)
                raise InvalidFeederError
            
        vertex_ids = [id for id in dataset["node"]["id"]]
        edge_ids = [id for id in dataset["transformer"]["id"]] + [id for id in dataset["line"]["id"]]
        edge_vertex_id_pairs = [id for id in zip(dataset["transformer"]["from_node"],
                                                 dataset["transformer"]["to_node"])] + [id for id in zip(dataset["line"]["from_node"], 
                                                                                                        dataset["line"]["to_node"])]
        status_enabled = [status for status in dataset["transformer"]["to_status"]] + [status for status in dataset["line"]["to_status"]]
        edge_enabled = [bool(status) for status in status_enabled]
        source_vertex_id = dataset["source"]["node"]
        grid = GraphProcessor(vertex_ids= vertex_ids, 
                       edge_ids= edge_ids, 
                       edge_vertex_id_pairs= edge_vertex_id_pairs, 
                       edge_enabled= edge_enabled, 
                       source_vertex_id= source_vertex_id)
        if not ev_pool.index.equals(active_load_profile.index):
            raise InvalidProfilesError
        if not active_load_profile.columns.equals(reactive_load_profile.columns):
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
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        self.feeder_ids = feeder_ids
        self.ev_pool = ev_pool
        
    
    def alternative_grid_topology(self, edge_id: int):
        if edge_id not in self.grid.edge_ids:
            raise IDNotFoundError
        id = np.asarray(self.input_data["line"]["id"] == edge_id).nonzero()[0].item()
        if self.input_data["line"]["from_status"][id] != [1] or self.input_data["line"]["to_status"][id] != [1] :
            raise LineNotFullyConnectedError
        model_rep = self.model.copy()
        update_line = initialize_array("update","line",1)
        update_line["id"] = [edge_id]
        update_line["from_status"] = [0]
        update_line["to_status"] = [0]
        model_rep.update(update_data={"line":update_line})
        alternative_lines = self.grid.find_alternative_edges(disabled_edge_id= edge_id)
        counter = 0
        max_loading = []
        max_loading_idx = []
        timestamps = []
        if alternative_lines:
            for line_id in alternative_lines:
                batch_model = model_rep.copy()
                update_line = initialize_array("update","line",1)
                update_line["id"] = [line_id]
                update_line["to_status"] = [1]
                update_data = {"line": update_line}
                batch_model.update(update_data= update_data)
                load_profile = initialize_array("update","sym_load",self.active_load_profile.shape)
                load_profile["id"] = self.active_load_profile.columns.to_numpy()
                load_profile["p_specified"] = self.active_load_profile.to_numpy()
                load_profile["q_specified"] = self.reactive_load_profile.to_numpy()
                update_data = {"sym_load": load_profile}
                assert_valid_batch_data(input_data= self.input_data,
                                        update_data= update_data,
                                        calculation_type= CalculationType.power_flow)
                output_data = batch_model.calculate_power_flow(update_data= update_data,
                                                                output_component_types= ["line"],
                                                                calculation_method=CalculationMethod.newton_raphson)
                max_loading.append(max(np.max(output_data["line"]["loading"],axis = 1)))
                max_loading_index = np.where(output_data["line"]["loading"] == max_loading[counter])
                max_loading_idx.append(int(self.input_data["line"]["id"][max_loading_index[1]]))
                timestamps.append(self.active_load_profile.index[max_loading_index[0]][0])
                counter = counter + 1
        df_result = pd.DataFrame(data= {"alternative_line_id": alternative_lines,
                                        "loading_max": max_loading,
                                        "loading_max_line_id": max_loading_idx,
                                        "timestamps": timestamps})
        return df_result
    

    def EV_penetration_level(self, penetration_level: int):
        total_houses = len(self.input_data["sym_load"]["id"])
        number_of_feeders = len(self.feeder_ids)
        nr_of_EV = floor(penetration_level * total_houses / number_of_feeders)
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
        for _ in range(len(ev_profiles)):
            ev_prof = self.ev_pool.iloc[:, ev_profiles[_]]
            self.active_load_profile[EV_ids[_]] = self.active_load_profile[EV_ids[_]] + ev_prof
        output = PowerGridModelling(data_path= self.input_data,
                                    active_load_profile_path= self.active_load_profile,
                                    reactive_load_profile_path= self.reactive_load_profile)
        df_result_u_pu = output.data_per_timestamp()
        df_result_loading_pu = output.data_per_line()
        return df_result_u_pu, df_result_loading_pu
