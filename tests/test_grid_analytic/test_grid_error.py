from power_system_simulation.grid_analytic import InvalidNumberOfTransformerError,InvalidNumberOfSourceError,InvalidProfilesError,InvalidFeederError,FeederIDNotUniqueError,IDNotFoundError,GridAnalysis
import pandas as pd
import pytest
from power_grid_model.utils import json_deserialize

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16,20]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"

#data_path = "tests/test_grid_analytic/big_network/input/input_network_data.json"
#feeder_ids = [1204,1304,1404,1504,1604,1704,1804,1904]
#active_path = "tests/test_grid_analytic/big_network/input/active_power_profile.parquet"
#reactive_path = "tests/test_grid_analytic/big_network/input/reactive_power_profile.parquet"
#ev_path = "tests/test_grid_analytic/big_network/input/ev_active_power_profile.parquet"

data_path_1 = "tests/test_grid_analytic/input_network_data_1.json"
data_path_2 = "tests/test_grid_analytic/input_network_data_2.json"
data_path_3 = "tests/test_grid_analytic/input_network_data_3.json"
# data_path_4 = "tests/test_grid_analytic/error_test_network/input_network_data_4.json"

def test_NumberOfTransformer():
    with pytest.raises(InvalidNumberOfTransformerError):
        data = GridAnalysis(data_path= data_path_1, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_NumberOfSource():
    with pytest.raises(InvalidNumberOfSourceError):
        data = GridAnalysis(data_path= data_path_2, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederID():
    feeder_ids_test = [16,25]
    with pytest.raises(InvalidFeederError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids_test, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederID_2():
    feeder_ids_test_2 = [16,16]
    with pytest.raises(FeederIDNotUniqueError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids_test_2, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_FeederFromNode():
    feeder_ids_test_3 = [16,17]
    with pytest.raises(InvalidFeederError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids_test_3, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_MatchingTimestamps():
    new_data = pd.read_parquet("tests/test_grid_analytic/active_power_profile.parquet")
    new_data.set_index(pd.date_range(start='2022-01-01 00:00:00', end='2022-01-10 23:45:00', freq='15min'), inplace= True)
    with pytest.raises(InvalidProfilesError):
        data = GridAnalysis(data_path= data_path, feeder_ids= feeder_ids, active_load_profile_path= new_data, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

def test_NumberofEVProfile():
    with pytest.raises(InvalidProfilesError):
        data = GridAnalysis(data_path= data_path_3, feeder_ids= feeder_ids, active_load_profile_path= active_path, reactive_load_profile_path= reactive_path, ev_pool_path= ev_path)

# test input data as dict and dataframes
def test_input_data():
    with open(data_path) as fp:
        data = fp.read()
    input_data = json_deserialize(data)
    active_load = pd.read_parquet(active_path)
    reactive_load = pd.read_parquet(reactive_path)
    ev_pool = pd.read_parquet(ev_path)
    result = GridAnalysis(data_path= input_data, 
                          feeder_ids= feeder_ids, 
                          active_load_profile_path= active_load, 
                          reactive_load_profile_path= reactive_load,
                          ev_pool_path= ev_pool)
    assert True

