from power_system_simulation.grid_analytic import GridAnalysis
import pandas as pd
data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"
result = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)
df_result = pd.DataFrame(result.alternative_grid_topology(edge_id= 22))
print(df_result)