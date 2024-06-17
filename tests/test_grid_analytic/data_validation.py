# # from power_grid_model.utils import (
# #     json_deserialize
# # )
# from power_system_simulation.power_grid_modelling import dataConversion as dc
# import pandas as pd
# import numpy as np

# # data_path = "tests/test_grid_analytic/meta_data.json"
# # with open(data_path) as fp:
# #     data = fp.read()
# # dataset = json_deserialize(data)
# # print(pd.DataFrame(dataset))
# # print(pd.read_parquet("tests/test_grid_analytic/ev_active_power_profile.parquet").columns.to_list())
# data = dc(data_path= "tests/test_grid_analytic/input_network_data.json",active_sym_load_path="tests/test_grid_analytic/active_power_profile.parquet", reactive_sym_load_path="tests/test_grid_analytic/reactive_power_profile.parquet")[0]
# print(pd.DataFrame(data=data["line"]))
