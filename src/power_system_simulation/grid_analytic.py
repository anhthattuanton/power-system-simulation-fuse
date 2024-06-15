from power_system_simulation.graph_processing import GraphProcessor


import numpy as np
import pandas as pd
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

from power_grid_model.utils import (
    json_deserialize, 
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

class IDNotUniqueError(Exception):
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
            data_path: str,
            feeder_ids: list[int],
            active_load_profile_path: str,
            reactive_load_profile_path: str,
            ev_pool_path: str
    ) -> None:
        with open(data_path) as fp:
            data = fp.read()
        dataset = json_deserialize(data= data)
        ev_pool = pd.read_parquet(ev_pool_path)
        active_load_profile = pd.read_parquet(active_load_profile_path)
        reactive_load_profile = pd.read_parquet(reactive_load_profile_path)
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
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        
    
    def alternative_grid_topology(self, edge_id: int):
        """
        In this functionality, the user would like to know alternative grid topology when a given line is out of service.
        The user will provide the Line ID which is going to be out of service.

        * If the given Line ID is not a valid `line`, raise proper error.
        * If the given Line ID is not connected at both sides in the base case (`from_status` and `to_status` should be both `1`), raise proper error.
        * You need to disconnect the designated line, set both `from_status` and `to_status` to `0`. And find list of Line IDs which are currently disconnected, and can be connected to make the grid fully connected again. Tip: use the graph function from Assignment 1.
        * For each alternative `line` to be connected (set `to_status` to `1`), run the time-series power flow for the whole time period.
        * Return a table to summarize the results, each row in the table is one alternative scenario. The following columns are needed:
        * The alternative Line ID to be connected
        * The maximum loading among of lines and timestamps
        * The Line ID of this maximum
        * The timestamp of this maximum
        * If there are no alternatives, it still should return an empty table with the correct data format and heading. You should test this behaviour in the unit tests.
        """
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

    
        
        
