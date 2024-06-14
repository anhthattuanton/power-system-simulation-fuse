from power_system_simulation.grid_analytic import InvalidNumberOfTransformerError,InvalidNumberOfSourceError,InvalidProfilesError,InvalidFeederError,IDNotUniqueError,IDNotFoundError,GridAnalysis
import pandas as pd
import pytest

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

data_path_1 = "tests/test_grid_analytic/error_test_network/input_network_data_1.json"
data_path_2 = "tests/test_grid_analytic/error_test_network/input_network_data_2.json"
data_path_3 = "tests/test_grid_analytic/error_test_network/input_network_data_3.json"
data_path_4 = "tests/test_grid_analytic/error_test_network/input_network_data_4.json"

def test_NumberOfTransformer():
    with pytest.raises(InvalidNumberOfTransformerError):
        data = GridAnalysis(data_path= data_path_1, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_NumberOfSource():
    with pytest.raises(InvalidNumberOfSourceError):
        data = GridAnalysis(data_path= data_path_2, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederID():
    feeder_ids_test = [16,25]
    with pytest.raises(IDNotFoundError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids_test, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederID_2():
    feeder_ids_test_2 = [16,16]
    with pytest.raises(IDNotUniqueError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids_test_2, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederFromNode():
    with pytest.raises(InvalidFeederError):
        data = GridAnalysis(data_path= data_path_3, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_MatchingTimestamps():
    with pytest.raises(InvalidProfilesError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_NumberofEVProfile():
    with pytest.raises(InvalidProfilesError):
        data = GridAnalysis(data_path= data_path_4, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_init():
    try: 
        GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)
    except Exception as e:
        pytest.fail(f"GrindAnalysis raised an exception: {e}")

def test_EV_penetration_level():
    data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)
    try:
        data.EV_penetration_level(0.5)
    except Exception as e:
        pytest.fail(f"GridAnalysis raised an exception: {e}")
