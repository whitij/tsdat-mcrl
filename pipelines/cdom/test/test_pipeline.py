import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_cdom_pipeline():
    config_path = Path("pipelines/cdom/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/cdom/test/data/input/20210805_230012_cdom.log"
    expected_file = "pipelines/cdom/test/data/expected/cdom.mcrl_pier-seabird_smp_1-5min.a1.20210805.160014.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
