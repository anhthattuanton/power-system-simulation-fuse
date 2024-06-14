from power_system_simulation.grid_analytic import GridAnalysis
import pandas as pd

data_path = "tests/test_grid_analytic/small_network/input/input_network_data.json"
feeder_ids = [16,20]
active_path = "tests/test_grid_analytic/small_network/input/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/small_network/input/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/small_network/input/ev_active_power_profile.parquet"

#data_path = "tests/test_grid_analytic/big_network/input/input_network_data.json"
#feeder_ids = [1204,1304,1404,1504,1604,1704,1804,1904]
#active_path = "tests/test_grid_analytic/big_network/input/active_power_profile.parquet"
#reactive_path = "tests/test_grid_analytic/big_network/input/reactive_power_profile.parquet"
#ev_path = "tests/test_grid_analytic/big_network/input/ev_active_power_profile.parquet"

result = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)
df_result_u_pu, df_result_loading_pu = result.EV_penetration_level(0.5)
print("u_pu results:")
print(df_result_u_pu)
print("loading results:")
print(df_result_loading_pu)