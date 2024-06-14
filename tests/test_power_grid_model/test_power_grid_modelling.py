import pytest
import math

from power_system_simulation.power_grid_modelling import dataConversion, powerGridModelling, InvalidProfilesError, dataValidation
import numpy as np
import warnings

with warnings.catch_warnings(action="ignore", category=DeprecationWarning):
    # suppress warning about pyarrow as future required dependency
    import pandas as pd

from power_grid_model import LoadGenType
from power_grid_model import PowerGridModel, CalculationMethod, CalculationType
from power_grid_model import initialize_array
from power_grid_model.validation import ValidationException

def test_invalid_input():
    with pytest.raises(ValidationException):
        data = dataConversion(data_path= "tests/test_power_grid_model/input_network_data_invalid.json", 
                              active_sym_load_path= "tests/test_power_grid_model/active_power_profile.parquet", 
                              reactive_sym_load_path= "tests/test_power_grid_model/reactive_power_profile.parquet")


data = dataConversion(data_path= "tests/test_power_grid_model/input_network_data.json", 
                    active_sym_load_path= "tests/test_power_grid_model/active_power_profile.parquet", 
                    reactive_sym_load_path= "tests/test_power_grid_model/reactive_power_profile.parquet")

def test_table1():
    result = powerGridModelling(dataset= data[0], active_load_profile= data[1], reactive_load_profile= data[2])
    expected_result = pd.read_parquet("tests/test_power_grid_model/output_table_row_per_timestamp.parquet")
    assert result[0].equals(expected_result)
  
def test_profiles_not_matching():
    new_data = data[2].copy()
    new_data.set_index(pd.date_range("2022-01-01", periods= 10, freq="h"), inplace= True)
    with pytest.raises(InvalidProfilesError):
        result = dataValidation(active_load_profile= data[1], reactive_load_profile= new_data)
