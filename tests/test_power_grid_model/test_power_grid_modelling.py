import pytest

from power_system_simulation.power_grid_modelling import InvalidProfilesError, PowerGridModelling
import numpy as np
import warnings

with warnings.catch_warnings(action="ignore", category=DeprecationWarning):
    # suppress warning about pyarrow as future required dependency
    import pandas as pd

from power_grid_model.validation import ValidationException

def test_invalid_input():
    with pytest.raises(ValidationException):
        result = PowerGridModelling(data_path= "tests/test_power_grid_model/input_network_data_invalid.json",
                                active_load_profile_path= "tests/test_power_grid_model/active_power_profile.parquet",
                                reactive_load_profile_path= "tests/test_power_grid_model/reactive_power_profile.parquet")

def test_table1():
    output = PowerGridModelling(data_path= "tests/test_power_grid_model/input_network_data.json",
                                active_load_profile_path= "tests/test_power_grid_model/active_power_profile.parquet",
                                reactive_load_profile_path= "tests/test_power_grid_model/reactive_power_profile.parquet")
    result = output.data_per_timestamp()
    expected_result = pd.read_parquet("tests/test_power_grid_model/output_table_row_per_timestamp.parquet")
    assert result.equals(expected_result)
  
def test_profiles_not_matching():
    new_data = pd.read_parquet("tests/test_power_grid_model/reactive_power_profile.parquet")
    new_data.set_index(pd.date_range("2022-01-01", periods= 10, freq="h"), inplace= True)
    new_data.to_parquet("tests/test_power_grid_model/reactive_power_profile_invalid.parquet")   
    with pytest.raises(InvalidProfilesError):
        output = PowerGridModelling(data_path= "tests/test_power_grid_model/input_network_data.json",
                                    active_load_profile_path= "tests/test_power_grid_model/active_power_profile.parquet",
                                    reactive_load_profile_path= "tests/test_power_grid_model/reactive_power_profile_invalid.parquet")
def test_table2():
    output = PowerGridModelling(data_path= "tests/test_power_grid_model/input_network_data.json",
                                active_load_profile_path= "tests/test_power_grid_model/active_power_profile.parquet",
                                reactive_load_profile_path= "tests/test_power_grid_model/reactive_power_profile.parquet")
    result = output.data_per_line()
    assert True