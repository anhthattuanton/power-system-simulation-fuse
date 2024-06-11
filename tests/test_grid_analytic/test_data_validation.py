from power_grid_model.utils import (
    json_deserialize
)
import pandas as pd

data_path = "tests/test_grid_analytic/meta_data.json"
with open(data_path) as fp:
    data = fp.read()
dataset = json_deserialize(data)
print(pd.DataFrame(dataset))