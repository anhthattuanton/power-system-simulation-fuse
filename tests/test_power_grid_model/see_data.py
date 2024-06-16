import pandas as pd
from power_system_simulation.grid_analytic import GridAnalysis

# df_result =  pd.read_parquet("tests/test_grid_analytic/active_power_profile.parquet")
# df_result1 =  pd.read_parquet("tests/test_grid_analytic/reactive_power_profile.parquet")
# print(type(df_result.columns))
# df_result.set_index(pd.date_range("2022-01-01", periods=10, freq="h"),inplace= True)
# print(df_result)
# print(df_result.index.tolist())
# df_result =  pd.read_parquet("tests/test_power_grid_model/reactive_power_profile.parquet")
# df_result.columns
# print(df_result[8][:]/1e5)

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16,20]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"
data_path_3 = "tests/test_grid_analytic/input_network_data_3.json"

data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)
