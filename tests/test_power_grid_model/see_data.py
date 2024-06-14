import pandas as pd
import math

df_result =  pd.read_parquet("tests/test_power_grid_model/active_power_profile.parquet")
print(df_result)
# df_result.set_index(pd.date_range("2022-01-01", periods=10, freq="h"),inplace= True)
# print(df_result)
# print(df_result.index.tolist())
df_result =  pd.read_parquet("tests/test_power_grid_model/reactive_power_profile.parquet")
# df_result.columns
print(df_result[8][:]/1e5)