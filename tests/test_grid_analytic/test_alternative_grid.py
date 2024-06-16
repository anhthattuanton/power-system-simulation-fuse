import numpy as np
import pandas as pd
import pytest
from power_grid_model.utils import json_deserialize_from_file

from power_system_simulation.grid_analytic import GridAnalysis, IDNotFoundError, LineNotFullyConnectedError

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"
result = GridAnalysis(
    data_path=data_path,
    feeder_ids=feeder_ids,
    active_load_profile_path=active_path,
    reactive_load_profile_path=reactive_path,
    ev_pool_path=ev_path,
)
# df_result = pd.DataFrame(result.alternative_grid_topology(edge_id= 22))
# print(df_result)


def test_alternative_grids():
    result.alternative_grid_topology(edge_id=22)
    assert True


def test_id_not_found():
    with pytest.raises(IDNotFoundError):
        result.alternative_grid_topology(edge_id=100)


def test_line_not_connected():
    input_data = json_deserialize_from_file(data_path)
    id = np.asarray(input_data["line"]["id"] == 22).nonzero()[0].item()
    input_data["line"]["from_status"][id] = 0
    data = GridAnalysis(
        data_path=input_data,
        feeder_ids=feeder_ids,
        active_load_profile_path=active_path,
        reactive_load_profile_path=reactive_path,
        ev_pool_path=ev_path,
    )
    with pytest.raises(LineNotFullyConnectedError):
        data.alternative_grid_topology(edge_id=22)
