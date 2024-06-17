import pandas as pd

"""
Copy test data path
"""
data_path = "tests/test_power-grid-model/input/input_network_data.json"
active_sym_load_path = "tests/test_power-grid-model/input/active_power_profile.parquet"
reactive_sym_load_path = "tests/test_power-grid-model/input/reactive_power_profile.parquet"
exp_per_line_path = "tests/test_power-grid-model/expected_output/output_table_row_per_line.parquet"
exp_per_timestamp_path = "tests/test_power-grid-model/expected_output/output_table_row_per_timestamp.parquet"

exp_per_line = pd.read_parquet(exp_per_line_path)
exp_per_timestamp = pd.read_parquet(exp_per_timestamp_path)

"""
For error handling tests, you can create your own dataset instead of the one provided to us above. Make test datasets guide is in the power grid
workshop examples 
"""
from power_system_simulation.power_grid_model_ass2 import powerGridModelling, dataConversion

dataset, active_load_profile, reactive_load_profile = dataConversion(data_path= data_path, active_sym_load_path= active_sym_load_path, reactive_sym_load_path= reactive_sym_load_path)
df_result_u_pu, df_result_loading_pu = powerGridModelling(dataset= dataset,active_load_profile= active_load_profile,reactive_load_profile= reactive_load_profile)
print("u_pu results:")
print(df_result_u_pu)
print(exp_per_timestamp)
print("loading results:")
print(df_result_loading_pu)
print(exp_per_line)
#import pandas as pd
# print(set(pd.read_parquet(active_sym_load_path).columns))
#print(type(pd.read_parquet(active_sym_load_path).index))