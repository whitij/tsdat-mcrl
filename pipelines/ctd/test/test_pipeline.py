import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close

# DEVELOPER: Update paths to your configuration(s), test input(s), and expected test
# results files.


def test_ctd_pipeline():
    config_path = Path("pipelines/ctd/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/ctd/test/data/input/ctd_20221027_192001.log"
    expected_file = "pipelines/ctd/test/data/expected/ctd.mcrl_pier-seabird_smp_1-5min.a1.20221027.122038.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
