import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_adcp_pipeline():
    config_path = Path("pipelines/adcp/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/adcp/test/data/input/hADCP_20220419_150320.wpr"
    expected_file = "pipelines/adcp/test/data/expected/adcp.mcrl_pier-nortek_awac_1-5min.a1.20220419.080313.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False, atol=1e-5)
