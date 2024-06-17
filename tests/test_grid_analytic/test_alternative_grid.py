import numpy as np
import pytest
from power_grid_model.utils import json_deserialize_from_file, json_serialize_to_file

from power_system_simulation.grid_analytic import GridAnalysis, IDNotFoundError, LineNotFullyConnectedError

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"
result = GridAnalysis(
    data= [data_path,active_path,reactive_path,ev_path], feeder_ids= feeder_ids
)

def test_alternative_grids():
    result.alternative_grid_topology(edge_id=22)
    assert True


def test_id_not_found():
    with pytest.raises(IDNotFoundError) as error:
        result.alternative_grid_topology(edge_id=100)
    assert str(error.value) == "Line ID provided is not in line IDs."


def test_line_not_connected():
    input_data = json_deserialize_from_file(data_path)
    id = np.asarray(input_data["line"]["id"] == 22).nonzero()[0].item()
    input_data["line"]["from_status"][id] = 0
    json_serialize_to_file(file_path= "tests/test_grid_analytic/input_network_data_4.json", data= input_data)
    result = GridAnalysis(
        data=["tests/test_grid_analytic/input_network_data_4.json",active_path,reactive_path,ev_path],
        feeder_ids= feeder_ids
    )
    with pytest.raises(LineNotFullyConnectedError) as error:
        result.alternative_grid_topology(edge_id=22)
    assert str(error.value) == "Line is not fully connected on both side."
