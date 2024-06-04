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
    load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
    load_profile["id"] = active_load_profile.columns.to_numpy()
    load_profile["p_specified"] = active_load_profile.to_numpy()
    load_profile["q_specified"] = reactive_load_profile.to_numpy()
    update_dataset = {"sym_load": load_profile}
    assert_valid_batch_data(input_data= dataset, update_data= update_dataset, calculation_type= CalculationType.power_flow)
    output_data = model.calculate_power_flow(update_data=update_dataset, calculation_method=CalculationMethod.newton_raphson)
    
    pass