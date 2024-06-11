# import 
import numpy as np
import pandas as pd

from power_grid_model import (
    # LoadGenType,
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
    json_deserialize
)

class InvalidProfilesError(Exception):
    pass

def dataConversion(
        data_path: str,
        active_sym_load_path: str,
        reactive_sym_load_path: str):
    with open(data_path) as fp:
        data = fp.read()
    dataset = json_deserialize(data)
    assert_valid_input_data(input_data= dataset, 
                            calculation_type= CalculationType.power_flow)
    active_load_profile = pd.read_parquet(active_sym_load_path)
    reactive_load_profile = pd.read_parquet(reactive_sym_load_path)
    if active_load_profile.index != reactive_load_profile.index:
        raise InvalidProfilesError
    return dataset, active_load_profile, reactive_load_profile

def powerGridModelling(
        dataset: dict,
        active_load_profile: pd.DataFrame,
        reactive_load_profile: pd.DataFrame):
    # with open(data_path) as fp0:
    #     data = fp0.read()
    # dataset = json_deserialize(data)
    # assert_valid_input_data(input_data= dataset, 
    #                         calculation_type= CalculationType.power_flow)
    # active_load_profile = pd.read_parquet(active_sym_load_path)
    # reactive_load_profile = pd.read_parquet(reactive_sym_load_path)
    # if not active_load_profile.index.equals(reactive_load_profile.index) or not active_load_profile.columns.equals(reactive_load_profile.columns):
    #     raise ProfilesNotMatching
    load_profile = initialize_array("update", "sym_load", active_load_profile.shape)
    load_profile["id"] = active_load_profile.columns.to_numpy()
    load_profile["p_specified"] = active_load_profile.to_numpy()
    load_profile["q_specified"] = reactive_load_profile.to_numpy()
    update_dataset = {"sym_load": load_profile}
    assert_valid_batch_data(input_data= dataset, 
                            update_data= update_dataset, 
                            calculation_type= CalculationType.power_flow)
    model = PowerGridModel(dataset)
    output_data = model.calculate_power_flow(update_data=update_dataset,
                                             calculation_method=CalculationMethod.newton_raphson)
    """
    1st table:
    """
    timestamps = active_load_profile.index
    df_u_pu = pd.DataFrame(output_data["node"]["u_pu"])
    arr_node_id = output_data["node"]["id"][0,:]
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
    df_result_node = pd.DataFrame(data={"Timestamp":timestamps,
                                   "u_pu_max":u_max,
                                   "Node_ID_max":max_node_id,
                                   "u_pu_min":u_min,
                                   "Node_ID_min":min_node_id})
    df_result_node.set_index("Timestamp",inplace=True)
    """
    2nd table:
    """
    
    # return 2 dataframes
    pass
    # max_voltage_idx = np.where(max(output_data["node"]["u_pu"]))
    # min_voltage_idx = np.where(min(output_data["node"]["u_pu"]))
    # max_voltage = output_data["node"]["u_pu"][max_voltage_idx]
    # min_voltage = output_data["node"]["u_pu"][min_voltage_idx]
    # max_voltage_id = output_data["node"]["id"][max_voltage_idx]
    # min_voltage_id = output_data["node"]["id"][min_voltage_idx]
    # frame = {max_voltage, max_voltage_id, min_voltage, min_voltage_id}
    # results_voltage = pd.DataFrame(data=frame,index=active_load_profile.index)
    # print(results_voltage)
    