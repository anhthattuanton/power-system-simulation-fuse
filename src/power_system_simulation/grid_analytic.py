import random
from math import floor
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from power_grid_model import (
    CalculationMethod,
    CalculationType,
    PowerGridModel,
    initialize_array,
)
from power_grid_model.utils import json_deserialize_from_file
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data

from power_system_simulation.graph_processing import GraphProcessor
from power_system_simulation.power_grid_modelling import PowerGridModelling


class InvalidNumberOfSourceError(Exception):
    """
    Number of source is more than 1
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class InvalidNumberOfTransformerError(Exception):
    """
    Number of transformer is more than 1
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class IDNotFoundError(Exception):
    """
    ID is not in the list of related ID
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class FeederIDNotUniqueError(Exception):
    """
    One or more ID of feeder IDs is duplicated
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class InvalidFeederError(Exception):
    """
    Feeder ID is invalid with node ID data
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class InvalidProfilesError(Exception):
    """
    Load profile is invalid
    """
    def __init__(self, error: str):
        self.error = error
        print(error)


class LineNotFullyConnectedError(Exception):
    """
    Grid is not fully connected
    """
    def __init__(self, error: str):
        self.error = error
        print(error)

def data_conversion(data: List[Union[str | Dict,
                        List[int],
                        str | pd.DataFrame,
                        str | pd.DataFrame,
                        str | pd.DataFrame]]):
    """
        say something
        """
    data_path = data[0]
    feeder_ids = data[1]
    active_load_profile_path = data[2]
    reactive_load_profile_path = data[3]
    ev_pool_path = data[4]
    if isinstance(data_path,str):
        dataset = json_deserialize_from_file(data_path)
        assert_valid_input_data(input_data=dataset, 
                                calculation_type=CalculationType.power_flow)
    else:
        dataset = data_path
    if isinstance(active_load_profile_path,str):
        active_load_profile = pd.read_parquet(active_load_profile_path)
    else:
        active_load_profile = active_load_profile_path
    if isinstance(reactive_load_profile_path,str):
        reactive_load_profile = pd.read_parquet(reactive_load_profile_path)
    else:
        reactive_load_profile = reactive_load_profile_path
    if isinstance(ev_pool_path, str):
        ev_pool = pd.read_parquet(ev_pool_path)
    else:
        ev_pool = ev_pool_path
    return dataset, feeder_ids, active_load_profile, reactive_load_profile, ev_pool

def simple_error_check(dataset: Dict[str, np.ndarray | Dict[str, np.ndarray]],
                       feeder_ids: list[int],
                       ):
    """
        say something
        """
    idx = []
    if len(dataset["source"]) != 1:
        raise InvalidNumberOfSourceError("Grid should only contain one source.")
    if len(dataset["transformer"]) != 1:
        raise InvalidNumberOfTransformerError("Grid should only contain one transformer.")
    if len(set(feeder_ids)) != len(feeder_ids):
        raise FeederIDNotUniqueError("Feeder IDs contains duplicated IDs.")
    for feeder_id in feeder_ids:
        if feeder_id not in dataset["line"]["id"]:
            raise InvalidFeederError("Feeder IDs contain invalid IDs.")    
    for feeder_id in feeder_ids:
        idx.append(np.asarray(dataset["line"]["id"] == feeder_id).nonzero()[0].item())
    for index in idx:
        if dataset["line"]["from_node"][index] not in dataset["transformer"]["to_node"]:
            raise InvalidFeederError("Feeder should be connected to transformer.")
        
def batch_data_assertion(dataset: Dict,
                         active_load_profile: pd.DataFrame,
                         reactive_load_profile: pd.DataFrame):
    """
        say something
        """
    if active_load_profile.index.equals(reactive_load_profile.index):
        raise InvalidProfilesError("Load profiles should have matching timestamps.")
    load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
    load_profile["id"] = active_load_profile.columns.to_numpy()
    load_profile["p_specified"] = active_load_profile.to_numpy()
    load_profile["q_specified"] = reactive_load_profile.to_numpy()
    update_dataset = {"sym_load": load_profile}
    assert_valid_batch_data(
        input_data=dataset, update_data=update_dataset, 
        calculation_type=CalculationType.power_flow
    )
    return update_dataset

def graph_creator(dataset: dict)->GraphProcessor:
    """
        say something
        """
    vertex_ids = list(dataset['node']['id'])
    edge_ids = list(dataset['transformer']['id'])
    edge_ids = edge_ids  + list(dataset['line']['id'])
    edge_vertex_id_pairs = list(zip(dataset['transformer']['from_node'], 
                                    dataset['transformer']['to_node']))
    status_enabled = list(dataset['transformer']['to_status'])
    status_enabled = status_enabled + list(dataset['line']['to_status'])
    edge_enabled = [bool(status) for status in status_enabled]
    source_vertex_id = dataset["source"]["node"]
    grid = GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id_pairs,
        edge_enabled=edge_enabled,
        source_vertex_id=source_vertex_id,
    )
    return grid

def load_profiles_assertion(dataset: Dict,
                            active_load_profile: pd.DataFrame,
                            reactive_load_profile: pd.DataFrame,
                            ev_pool: pd.DataFrame):
    """
        say something
        """
    if not ev_pool.index.equals(active_load_profile.index):
        raise InvalidProfilesError(
            "EV pool and load profiles should have matching timestamps.")
    if not active_load_profile.index.equals(reactive_load_profile.index):
        raise InvalidProfilesError(
            "Active and reative load profile should have matching timestamps.")
    if not active_load_profile.columns.equals(reactive_load_profile.columns):
        raise InvalidProfilesError(
            "Active and reactive load profile should contain matching sym loads.")
    if not set(active_load_profile.columns).issubset(set(dataset["sym_load"]["id"])):
        raise InvalidProfilesError(
            "Active and reactive load profile should contain valid sym loads.")
    # The number of EV charging profile is at least the same as the number of sym_load.
    if len(ev_pool.columns.to_list()) < len(list(dataset["sym_load"]["id"])):
        raise InvalidProfilesError(
            "Number of EV profile should be at least the same as number of sym load.")

def alternative_grid_error(grid: GraphProcessor,
                           input_data,
                           edge_id: int):
    if edge_id not in grid.edge_ids:
        raise IDNotFoundError("Line ID provided is not in line IDs.")
    edge_index = np.asarray(input_data["line"]["id"] == edge_id).nonzero()[0].item()
    if (input_data["line"]["from_status"][edge_index] != [1] 
        or input_data["line"]["to_status"][edge_index] != [1]):
        raise LineNotFullyConnectedError("Line is not fully connected on both side.")

class GridAnalysis:
    """
    Build a package with some low voltage (LV) grid analytics functions.
    """
    def __init__(
        self,
        data: List[Union[(str | Dict),
                   (List[int]),
                   (str | pd.DataFrame),
                   (str | pd.DataFrame),
                   (str | pd.DataFrame)]]
    ) -> None:
        """
        Input:
        * A LV grid in PGM input format
        * The grid has one MV/LV transformer.
        * The grid is constructed in meshed (ring) structure, but some lines are disconnected
          (`to_status` is `0`), so that its base state is in a tree-structure.
        * The grid consists of many `sym_load`, each representing one LV household. There are 
        also many nodes without any `sym_load`.
        * LV feeder IDs: a list of line IDs which are the beginning of the LV feeders.
        * A (active and reactive) load profile of all the `sym_load` in the grid for certain
          time period.
        * In the same format as in [Assignment 2](../assignment_2/README.md#input-data)
        * A pool of EV charging profiles for the same time period as the time period of load
          profile.
        * The profiles provide the active power curve per EV.
        * The reactive power is assumed to be always zero.
        * The number of profiles is at least as many as the number of `sym_load` in the grid.
        """
        # # unzip:
        # data_path = data[0]
        # feeder_ids = data[1]
        # active_load_profile_path = data[2]
        # reactive_load_profile_path = data[3]
        # ev_pool_path = data[4]
        # if isinstance(data_path,str):
        #     dataset = json_deserialize_from_file(data_path)
        #     assert_valid_input_data(input_data=dataset, 
        #                             calculation_type=CalculationType.power_flow)
        # else:
        #     dataset = data_path
        # if isinstance(active_load_profile_path,str):
        #     active_load_profile = pd.read_parquet(active_load_profile_path)
        # else:
        #     active_load_profile = active_load_profile_path
        # if isinstance(reactive_load_profile_path,str):
        #     reactive_load_profile = pd.read_parquet(reactive_load_profile_path)
        # else:
        #     reactive_load_profile = reactive_load_profile_path
        data_unzipped = data_conversion(data= data)
        dataset = data_unzipped[0]
        feeder_ids = data_unzipped[1]
        active_load_profile = data[2]
        reactive_load_profile = data[3]
        ev_pool = data[4]
        simple_error_check(dataset= dataset, feeder_ids= feeder_ids)
        batch_data_assertion(dataset= dataset, 
                             active_load_profile= active_load_profile,
                             reactive_load_profile= reactive_load_profile)
        # if active_load_profile.index.equals(reactive_load_profile.index):
        #     raise InvalidProfilesError("Load profiles should have matching timestamps.")
        # load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
        # load_profile["id"] = active_load_profile.columns.to_numpy()
        # load_profile["p_specified"] = active_load_profile.to_numpy()
        # load_profile["q_specified"] = reactive_load_profile.to_numpy()
        # update_dataset = {"sym_load": load_profile}
        # assert_valid_batch_data(
        #     input_data=dataset, update_data=update_dataset, 
        #     calculation_type=CalculationType.power_flow
        # )
        # if isinstance(ev_pool_path, str):
        #     ev_pool = pd.read_parquet(ev_pool_path)
        # else:
        #     ev_pool = ev_pool_path
        # idx = []
        # if len(dataset["source"]) != 1:
        #     raise InvalidNumberOfSourceError("Grid should only contain one source.")
        # if len(dataset["transformer"]) != 1:
        #     raise InvalidNumberOfTransformerError("Grid should only contain one transformer.")
        # feeder_id_check(dataset= dataset, feeder_ids= feeder_ids)
        # for feeder_id in feeder_ids:
        #     idx.append(np.asarray(dataset["line"]["id"] == feeder_id).nonzero()[0].item())
        # for index in idx:
        #     if dataset["line"]["from_node"][index] not in dataset["transformer"]["to_node"]:
        #         raise InvalidFeederError("Feeder should be connected to transformer.")
        

        # vertex_ids = list(dataset['node']['id'])
        # edge_ids = list(dataset['transformer']['id'])
        # edge_ids = edge_ids  + list(dataset['line']['id'])
        # edge_vertex_id_pairs = list(zip(dataset['transformer']['from_node'], 
        #                                 dataset['transformer']['to_node']))
        # status_enabled = list(dataset['transformer']['to_status'])
        # status_enabled = status_enabled + list(dataset['line']['to_status'])
        # edge_enabled = [bool(status) for status in status_enabled]
        # source_vertex_id = dataset["source"]["node"]
        # grid = GraphProcessor(
        #     vertex_ids=vertex_ids,
        #     edge_ids=edge_ids,
        #     edge_vertex_id_pairs=edge_vertex_id_pairs,
        #     edge_enabled=edge_enabled,
        #     source_vertex_id=source_vertex_id,
        # )
        grid = graph_creator(dataset= dataset)
        # if not ev_pool.index.equals(active_load_profile.index):
        #     raise InvalidProfilesError(
        #         "EV pool and load profiles should have matching timestamps.")
        # if not active_load_profile.index.equals(reactive_load_profile.index):
        #     raise InvalidProfilesError(
        #         "Active and reative load profile should have matching timestamps.")
        # if not active_load_profile.columns.equals(reactive_load_profile.columns):
        #     raise InvalidProfilesError(
        #         "Active and reactive load profile should contain matching sym loads.")
        # if not set(active_load_profile.columns).issubset(set(dataset["sym_load"]["id"])):
        #     raise InvalidProfilesError(
        #         "Active and reactive load profile should contain valid sym loads.")
        # # The number of EV charging profile is at least the same as the number of sym_load.
        # if len(ev_pool.columns.to_list()) < len(list(dataset["sym_load"]["id"])):
        #     raise InvalidProfilesError(
        #         "Number of EV profile should be at least the same as number of sym load.")
        load_profiles_assertion(dataset= dataset,
                                active_load_profile= active_load_profile,
                                reactive_load_profile= reactive_load_profile,
                                ev_pool= ev_pool)
        model = PowerGridModel(dataset)
        self.input_data = dataset
        self.model = model
        self.grid = grid
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        self.feeder_ids = feeder_ids
        self.ev_pool = ev_pool

    def alternative_grid_topology(self, edge_id: int):
        """
        say something
        """
        alternative_grid_error(grid= self.grid,
                               input_data= self.input_data,
                               edge_id= edge_id)
        model_rep = self.model.copy()
        update_line = initialize_array("update", "line", 1)
        update_line["id"] = [edge_id]
        update_line["from_status"] = [0]
        update_line["to_status"] = [0]
        model_rep.update(update_data={"line": update_line})
        alternative_lines = self.grid.find_alternative_edges(disabled_edge_id=edge_id)
        counter = 0
        max_loading = []
        max_loading_idx = []
        timestamps = []
        if alternative_lines:
            for line_id in alternative_lines:
                batch_model = model_rep.copy()
                update_line = initialize_array("update", "line", 1)
                update_line["id"] = [line_id]
                update_line["to_status"] = [1]
                update_data = {"line": update_line}
                batch_model.update(update_data=update_data)
                load_profile = initialize_array("update", "sym_load", 
                                                self.active_load_profile.shape)
                load_profile["id"] = self.active_load_profile.columns.to_numpy()
                load_profile["p_specified"] = self.active_load_profile.to_numpy()
                load_profile["q_specified"] = self.reactive_load_profile.to_numpy()
                update_data = {"sym_load": load_profile}
                assert_valid_batch_data(
                    input_data=self.input_data, 
                    update_data=update_data, 
                    calculation_type=CalculationType.power_flow
                )
                output_data = batch_model.calculate_power_flow(
                    update_data=update_data,
                    output_component_types=["line"],
                    calculation_method=CalculationMethod.newton_raphson,
                )
                max_loading.append(max(np.max(output_data["line"]["loading"], axis=1)))
                max_loading_index = np.where(output_data["line"]["loading"] == max_loading[counter])
                max_loading_idx.append(int(self.input_data["line"]["id"][max_loading_index[1]]))
                timestamps.append(self.active_load_profile.index[max_loading_index[0]][0])
                counter = counter + 1
        df_result = pd.DataFrame(
            data={
                "alternative_line_id": alternative_lines,
                "loading_max": max_loading,
                "loading_max_line_id": max_loading_idx,
                "timestamps": timestamps,
            }
        )
        return df_result

    def ev_penetration_level(self, penetration_level: int):
        """
        say something
        """
        total_houses = len(self.input_data["sym_load"]["id"])
        number_of_feeders = len(self.feeder_ids)
        number_of_ev = floor(penetration_level * total_houses / number_of_feeders)
        ev_ids = []
        for n in self.feeder_ids:
            nodes_feeder = self.grid.find_downstream_vertices(n)
            loads_feeder = []
            for m in nodes_feeder:
                if m in self.input_data["sym_load"]["node"]:
                    load_idx = np.where(self.input_data["sym_load"]["node"] == m)
                    loads_feeder.extend(list(self.input_data["sym_load"]["id"][load_idx]))
            ev_ids.extend(random.sample(loads_feeder, number_of_ev))
        ev_profiles = random.sample(list(self.ev_pool.columns), len(ev_ids))
        for _ in range(len(ev_profiles)):
            ev_prof = self.ev_pool.iloc[:, ev_profiles[_]]
            self.active_load_profile[ev_ids[_]] = self.active_load_profile[ev_ids[_]] + ev_prof
        output = PowerGridModelling(
            data_path=self.input_data,
            active_load_profile_path=self.active_load_profile,
            reactive_load_profile_path=self.reactive_load_profile,
        )
        df_result_u_pu = output.data_per_timestamp()
        df_result_loading_pu = output.data_per_line()
        return df_result_u_pu, df_result_loading_pu
