# import 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

from power_grid_model import (
    LoadGenType,
    PowerGridModel,
    CalculationType,
    CalculationMethod,
    initialize_array
)

from power_grid_model.validation import (
    assert_valid_input_data,
    assert_valid_batch_data
)

from power_grid_model.utils import (
    json_deserialize, 
    json_serialize
)

class InvalidProfilesError(Exception):
    pass

class PowerGridModelling:
    def __init__(self,
                 data_path: str,
                 active_load_profile_path: str,
                 reactive_load_profile_path: str) -> None:
        with open(data_path) as fp:
            data = fp.read()
        dataset = json_deserialize(data= data)
        assert_valid_input_data(input_data= dataset,
                                calculation_type= CalculationType.power_flow)
        active_load_profile = pd.read_parquet(active_load_profile_path)
        reactive_load_profile = pd.read_parquet(reactive_load_profile_path)
        if active_load_profile.index.to_list() != reactive_load_profile.index.to_list():
            raise InvalidProfilesError
        model = PowerGridModel(dataset)
        load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
        load_profile["id"] = active_load_profile.columns.to_numpy()
        load_profile["p_specified"] = active_load_profile.to_numpy()
        load_profile["q_specified"] = reactive_load_profile.to_numpy()
        update_dataset = {"sym_load": load_profile}
        assert_valid_batch_data(input_data= dataset, 
                            update_data= update_dataset, 
                            calculation_type= CalculationType.power_flow)
        output_data = model.calculate_power_flow(update_data=update_dataset,
                                                calculation_method=CalculationMethod.newton_raphson)
        self.model = model
        self.output_data = output_data
        self.active_load_profile = active_load_profile
        self.reactive_load_profile = reactive_load_profile
        self.timestamps = active_load_profile.index

    def data_per_timestamp(self)-> pd.DataFrame:
        df_u_pu = pd.DataFrame(self.output_data["node"]["u_pu"])
        arr_node_id = self.output_data["node"]["id"][0,:]
        u_idx_max = np.argmax(df_u_pu,axis= 1)
        u_max = np.max(df_u_pu,axis= 1)
        u_idx_min = np.argmin(df_u_pu,axis= 1)
        u_min = np.min(df_u_pu,axis= 1)
        max_node_id = []
        min_node_id = []
        for n in u_idx_max:
            max_node_id.append(arr_node_id[n])
        for m in u_idx_min:
            min_node_id.append(arr_node_id[m])
        df_result_node = pd.DataFrame(data={"Max_Voltage":u_max.to_numpy(),
                                    "Max_Voltage_Node":max_node_id,
                                    "Min_Voltage":u_min.to_numpy(),
                                    "Min_Voltage_Node":min_node_id},
                                    index=self.timestamps)
        df_result_node.index.name = "Timestamp"
        return df_result_node

    def data_per_line(self)-> pd.DataFrame:
        df_loading_pu = pd.DataFrame(self.output_data["line"]["loading"])
        arr_line_id = self.output_data["line"]["id"][0,:]
        loading_idx_max = np.argmax(df_loading_pu,axis= 0)
        loading_max = np.max(df_loading_pu,axis= 0)
        loading_idx_min = np.argmin(df_loading_pu,axis= 0)
        loading_min = np.min(df_loading_pu,axis= 0)
        max_line_timestamp = []
        min_line_timestamp = []
        for n in loading_idx_max:
            max_line_timestamp.append(self.timestamps[n])
        for m in loading_idx_min:
            min_line_timestamp.append(self.timestamps[m])
        df_result_line = pd.DataFrame(data={"Max_loading":loading_max.to_numpy(),
                                    "Max_Loading_Timestamp":max_line_timestamp,
                                    "Min_Loading":loading_min.to_numpy(),
                                    "Min_Loading_Timestamp":min_line_timestamp},
                                    index=arr_line_id)
        df_result_line.index.name = "Line_ID"
        return df_result_line
