import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_met_pipeline():
    config_path = Path("pipelines/met/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/met/test/data/input/met_20221007_100512.log"
    expected_file = "pipelines/met/test/data/expected/met.mcrl_pier-campbell_cr1000_1-5min.a1.20221007.030000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
