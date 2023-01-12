import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_hydrophone_pipeline():
    config_path = Path("pipelines/hydrophone/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/hydrophone/test/data/input/SCF_1856_20220105_001458.txt"
    expected_file = "pipelines/hydrophone/test/data/expected/hydrophone.mcrl_pier-oceansonics_iclisten_1-15min.a1.20220105.001458.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
