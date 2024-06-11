"""
Copy test data path
"""
data_path = "tests/test_power_grid_model/input_network_data.json"
active_sym_load_path = "tests/test_power_grid_model/active_power_profile.parquet"
reactive_sym_load_path = "tests/test_power_grid_model/reactive_power_profile.parquet"

"""
For error handling tests, you can create your own dataset instead of the one provided to us above. Make test datasets guide is in the power grid
workshop examples 
"""
# from power_system_simulation.power_grid_model import powerGridModelling, dataConversion

# dataset, active_load_profile, reactive_load_profile = dataConversion(data_path= data_path, active_sym_load_path= active_sym_load_path, reactive_sym_load_path= reactive_sym_load_path)
# df_result = powerGridModelling(dataset= dataset,active_load_profile= active_load_profile,reactive_load_profile= reactive_load_profile)
# print(df_result)
import pandas as pd
# print(set(pd.read_parquet(active_sym_load_path).columns))
print(pd.read_parquet("tests/test_grid_analytic/ev_active_power_profile.parquet").index)