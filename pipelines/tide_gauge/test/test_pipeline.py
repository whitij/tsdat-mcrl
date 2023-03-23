import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_tidegauge_pipeline():
    config_path = Path("pipelines/tide_gauge/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/tide_gauge/test/data/input/tidegage_20210801_000502.log"
    expected_file = "pipelines/tide_gauge/test/data/expected/tide_gauge.mcrl_pier-ysi_nile_1-5min.a1.20210731.170517.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_time_change():
    config_path = Path("pipelines/tide_gauge/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/tide_gauge/test/data/input/tidegage_20230105_232001.log"
    test_file2 = "pipelines/tide_gauge/test/data/input/tidegage_20230105_233502.log"

    dataset = pipeline.run([test_file])
    dataset2 = pipeline.run([test_file2])

    assert str(dataset.time[-1].values) == "2023-01-05T23:30:16.949000000"
    assert str(dataset2.time[-1].values) == "2023-01-05T23:45:16.509000000"
