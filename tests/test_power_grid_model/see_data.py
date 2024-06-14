import pandas as pd
import math

df_result =  pd.read_parquet("tests/test_power_grid_model/output_table_row_per_line.parquet")
print(df_result)
# df_result.set_index(pd.date_range("2022-01-01", periods=10, freq="h"),inplace= True)
# print(df_result)
# print(df_result.index.tolist())
# df_result =  pd.read_parquet("tests/test_power_grid_model/reactive_power_profile.parquet")
# df_result.columns
# print(df_result[8][:]/1e5)

from power_system_simulation.power_grid_modelling import powerGridModelling, dataConversion

# dataset, active_load_profile, reactive_load_profile = dataConversion(data_path= data_path, active_sym_load_path= active_sym_load_path, reactive_sym_load_path= reactive_sym_load_path)
# df_result = powerGridModelling(dataset= dataset,active_load_profile= active_load_profile,reactive_load_profile= reactive_load_profile)
# print(df_result)
data_path = "tests/test_power_grid_model/input_network_data.json"
active_sym_load_path = "tests/test_power_grid_model/active_power_profile.parquet"
reactive_sym_load_path = "tests/test_power_grid_model/reactive_power_profile.parquet"

import pandas as pd
# print(set(pd.read_parquet(active_sym_load_path).columns))
# print(pd.read_parquet("tests/test_grid_analytic/ev_active_power_profile.parquet").index)
dataset, active_load_profile, reactive_load_profile = dataConversion(data_path= data_path, active_sym_load_path= active_sym_load_path, reactive_sym_load_path= reactive_sym_load_path)
df_result = powerGridModelling(dataset= dataset,active_load_profile= active_load_profile,reactive_load_profile= reactive_load_profile)
print(df_result[0])
# print(df_result[1])