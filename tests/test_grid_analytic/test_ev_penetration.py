from power_system_simulation.grid_analytic import GridAnalysis

data_path = "tests/test_grid_analytic/input_network_data.json"
feeder_ids = [16, 20]
active_path = "tests/test_grid_analytic/active_power_profile.parquet"
reactive_path = "tests/test_grid_analytic/reactive_power_profile.parquet"
ev_path = "tests/test_grid_analytic/ev_active_power_profile.parquet"


def test_EV_penetration_level():
    data = GridAnalysis(
        data_path=data_path,
        feeder_ids=feeder_ids,
        active_load_profile_path=active_path,
        reactive_load_profile_path=reactive_path,
        ev_pool_path=ev_path,
    )
    data.EV_penetration_level(0.5)
    assert True
