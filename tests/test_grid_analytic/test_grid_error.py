import pandas as pd
import pytest
from power_grid_model.utils import json_deserialize

from power_system_simulation.grid_analytic import (
    FeederIDNotUniqueError,
    GridAnalysis,
    InvalidFeederError,
    InvalidNumberOfSourceError,
    InvalidNumberOfTransformerError,
    InvalidProfilesError,
)

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16, 20]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"

# data_path = "tests/test_grid_analytic/big_network/input/input_network_data.json"
# feeder_ids = [1204,1304,1404,1504,1604,1704,1804,1904]
# active_path = "tests/test_grid_analytic/big_network/input/active_power_profile.parquet"
# reactive_path = "tests/test_grid_analytic/big_network/input/reactive_power_profile.parquet"
# ev_path = "tests/test_grid_analytic/big_network/input/ev_active_power_profile.parquet"

data_path_1 = "tests/test_grid_analytic/input_network_data_1.json"
data_path_2 = "tests/test_grid_analytic/input_network_data_2.json"
data_path_3 = "tests/test_grid_analytic/input_network_data_3.json"
active_invalid_path = "tests/test_grid_analytic/active_power_profile_invalid.parquet"
# data_path_4 = "tests/test_grid_analytic/error_test_network/input_network_data_4.json"


def test_NumberOfTransformer():
    with pytest.raises(InvalidNumberOfTransformerError) as error:
        data = GridAnalysis(data=[data_path_1, active_path, reactive_path, ev_path], feeder_ids=feeder_ids)
    assert str(error.value) == "Grid should only contain one transformer."


def test_NumberOfSource():
    with pytest.raises(InvalidNumberOfSourceError) as error:
        data = GridAnalysis(data=[data_path_2, active_path, reactive_path, ev_path], feeder_ids=feeder_ids)
    assert str(error.value) == "Grid should only contain one source."


def test_FeederID():
    feeder_ids_test = [16, 25]
    with pytest.raises(InvalidFeederError) as error:
        data = GridAnalysis(data=[data_path, active_path, reactive_path, ev_path], feeder_ids=feeder_ids_test)
    assert str(error.value) == "Feeder IDs contain invalid IDs."


def test_FeederID_2():
    feeder_ids_test_2 = [16, 16]
    with pytest.raises(FeederIDNotUniqueError) as error:
        data = GridAnalysis(data=[data_path, active_path, reactive_path, ev_path], feeder_ids=feeder_ids_test_2)
    assert str(error.value) == "Feeder IDs contains duplicated IDs."


def test_FeederFromNode():
    feeder_ids_test_3 = [16, 17]
    with pytest.raises(InvalidFeederError) as error:
        data = GridAnalysis(data=[data_path, active_path, reactive_path, ev_path], feeder_ids=feeder_ids_test_3)
    assert str(error.value) == "Feeder should be connected to transformer."


def test_MatchingTimestamps():
    new_data = pd.read_parquet(active_path)
    new_data.set_index(
        pd.date_range(start="2022-01-01 00:00:00", end="2022-01-10 23:45:00", freq="15min"), inplace=True
    )
    new_data.to_parquet(active_invalid_path)
    with pytest.raises(InvalidProfilesError) as error:
        data = GridAnalysis(data=[data_path, active_invalid_path, reactive_path, ev_path], feeder_ids=feeder_ids)
    assert str(error.value) == "Load profiles should have matching timestamps."


def test_NumberofEVProfile():
    with pytest.raises(InvalidProfilesError) as error:
        data = GridAnalysis(data=[data_path_3, active_path, reactive_path, ev_path], feeder_ids=feeder_ids)
    assert str(error.value) == "Number of EV profile should be at least the same as number of sym load."


def test_matching_time_stamps_ev():
    new_data = pd.read_parquet(ev_path)
    new_data.set_index(
        pd.date_range(start="2022-01-01 00:00:00", end="2022-01-10 23:45:00", freq="15min"), inplace=True
    )
    new_data.to_parquet(active_invalid_path)
    with pytest.raises(InvalidProfilesError) as error:
        data = GridAnalysis(data=[data_path, active_path, reactive_path, active_invalid_path], feeder_ids=feeder_ids)
    assert str(error.value) == "EV pool and load profiles should have matching timestamps."


# test input data as dict and dataframes
# def test_input_data():
#     with open(data_path) as fp:
#         data = fp.read()
#     input_data = json_deserialize(data)
#     active_load = pd.read_parquet(active_path)
#     reactive_load = pd.read_parquet(reactive_path)
#     ev_pool = pd.read_parquet(ev_path)
#     result = GridAnalysis(
#         data_path=input_data,
#         feeder_ids=feeder_ids,
#         active_load_profile_path=active_load,
#         reactive_load_profile_path=reactive_load,
#         ev_pool_path=ev_pool,
#     )
#     assert True
