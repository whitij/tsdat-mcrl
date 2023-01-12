import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_par_pipeline():
    config_path = Path("pipelines/par/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/par/test/data/input/par_20211029_180000.log"
    expected_file = "pipelines/par/test/data/expected/par.mcrl_pier-licor_li193_1-15min.a1.20211029.180000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
