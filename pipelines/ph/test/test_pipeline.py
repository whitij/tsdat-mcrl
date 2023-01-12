import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_ph_pipeline():
    config_path = Path("pipelines/ph/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/ph/test/data/input/ph_20210813_160005.txt"
    expected_file = "pipelines/ph/test/data/expected/ph_.mcrl_pier-onset_mx2501_1-5min.a1.20210813.154505.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
