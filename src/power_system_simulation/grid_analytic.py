from power_system_simulation.graph_processing import GraphProcessor
from power_system_simulation.power_grid_modelling import powerGridModelling,dataConversion

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
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        
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
        # batch = []
        counter = 0
        max_loading = []
        max_loading_idx = []
        timestamps = []
        if alternative_lines:
            # update_lines = initialize_array("update","line",(len(alternative_lines),1))
            # update_lines["id"] = [[id] for id in alternative_lines]
            # update_lines["to_status"] = [[1] for n in alternative_lines]
            # output_data = model_rep.calculate_power_flow(update_data= {"line":update_lines},
            #                                              output_component_types= "line",
            #                                              calculation_method= CalculationMethod.newton_raphson,
            #                                              threading= 0)
            # max_loading = np.max(output_data["line"]["loading"], axis= 1)
            # max_loading_index = np.argmax(output_data["line"]["loading"], axis= 1)
            # loading_index = output_data["line"]["id"][0,:]
            # max_loading_idx = [loading_index[n] for n in max_loading_index]
            # df_result = pd.DataFrame(data= {"Alternative_line_ID": alternative_lines,
            #                                 "Loading_max": max_loading,
            #                                 "Max_loading_line_ID": max_loading_idx,
            #                                 })
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
                # max_loading_index = np.argmax(output_data["line"]["loading"], axis= 1)
                max_loading_index = np.where(output_data["line"]["loading"] == max_loading[counter])
                # loading_index = output_data["line"]["id"][0,:]
                # max_loading_idx[counter] = [loading_index[n] for n in max_loading_index]
                max_loading_idx.append(int(self.input_data["line"]["id"][max_loading_index[1]]))
                timestamps.append(self.active_load_profile.index[max_loading_index[0]][0])
                counter = counter + 1
        df_result = pd.DataFrame(data= {"alternative_line_id": alternative_lines,
                                        "loading_max": max_loading,
                                        "loading_max_line_id": max_loading_idx,
                                        "timestamps": timestamps})
        return df_result
    pass
    
        
        
