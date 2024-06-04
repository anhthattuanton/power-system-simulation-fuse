import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

from power_grid_model import (
    PowerGridModel,
    CalculationType,
    CalculationMethod,
    initialize_array
)

from power_grid_model.validation import (
    assert_valid_input_data,
    assert_valid_batch_data
)

class ProfilesNotMatching(Exception):
    pass

def powerGridModelling(
        data_path: str,
        active_sym_load_path: str,
        reactive_sym_load_path: str) -> None:
    with open(data_path) as fp0:
        data = fp0.read()
    dataset = json_deserialize(data)
    assert_valid_input_data(input_data= dataset, calculation_type= CalculationType.power_flow)
    model = PowerGridModel(dataset)
    active_load_profile = pd.read_parquet(active_sym_load_path)
    reactive_load_profile = pd.read_parquet(reactive_sym_load_path)
    if not active_load_profile.index.equals(reactive_load_profile.index) or not active_load_profile.columns.equals(reactive_load_profile.columns):
        raise ProfilesNotMatching
    load_profile = initialize_array("update", "sym_load", active_load_profile)
    load_profile["id"] = active_load_profile.columns.to_numpy()
    load_profile["p_specified"] = active_load_profile.to_numpy()
    load_profile["q_specified"] = reactive_load_profile.to_numpy()
    update_dataset = {"sym_load": load_profile}
    assert_valid_batch_data(input_data= dataset, update_data= update_dataset, calculation_type= CalculationType.power_flow)
    
    max_voltage_idx = np.where(max(output_data["node"]["u_pu"]))
    min_voltage_idx = np.where(min(output_data["node"]["u_pu"]))
    max_voltage = output_data["node"]["u_pu"][max_voltage_idx]
    min_voltage = output_data["node"]["u_pu"][min_voltage_idx]
    max_voltage_id = output_data["node"]["id"][max_voltage_idx]
    min_voltage_id = output_data["node"]["id"][min_voltage_idx]
    frame = {max_voltage, max_voltage_id, min_voltage, min_voltage_id}
    results_voltage = pd.DataFrame(data=frame)
