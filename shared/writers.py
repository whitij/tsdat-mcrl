import pandas as pd
import xarray as xr
from pathlib import Path
from pydantic import BaseModel, Extra
from typing import Any, Dict, List, Optional

from tsdat import FileWriter
from tsdat.config.storage import StorageConfig
from tsdat.config.utils import recursive_instantiate


def write_parquet(dataset, instrument):
    parameters = {
        "bucket": "mcrl-data-test",
        "region": "us-west-2",
        "storage_root": instrument,
        "data_folder": "parquet",
        "data_storage_path": Path(
            "{storage_root}/{datastream}/{data_folder}/year={year}/month={month}/day={day}"
        ),
    }
    storage_model = StorageConfig(
        classname="tsdat.io.storage.FileSystemS3", parameters=parameters
    )
    storage = recursive_instantiate(storage_model)
    storage.handler.writer = MCRLdataParquetWriter()

    storage.save_data(dataset)


class MCRLdataParquetWriter(FileWriter):
    """---------------------------------------------------------------------------------
    Writes the dataset to a parquet file.

    Converts a `xr.Dataset` object to a pandas `DataFrame` and saves the result to a
    parquet file using `pd.DataFrame.to_parquet()`. Properties under the
    `to_parquet_kwargs` parameter are passed to `pd.DataFrame.to_parquet()` as keyword
    arguments.

    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        dim_order: Optional[List[str]] = None
        to_parquet_kwargs: Dict[str, Any] = {}
        to_parquet_kwargs.update(dict(engine="pyarrow"))

    parameters: Parameters = Parameters()
    file_extension: str = ".parquet"

    def write(
        self, dataset: xr.Dataset, filepath: Optional[Path] = None, **kwargs: Any
    ) -> None:

        ds = dataset
        if len(ds.dims) > 1:
            if "iclisten" in ds.datastream:  # special handling for hydrophone
                df = pd.DataFrame(
                    {"time": ds["time"], "spl": ds["SPL"], "spl_qc": ds["qc_SPL"]}
                )
            elif "adcp" in ds.datastream:  # special handling for ADCP
                maxU = ds["U_mag"].max(dim="range")
                qc = (
                    ds["qc_U_mag"]
                    .where(ds["U_mag"] == ds["U_mag"].max(dim="range"))
                    .sum(dim="range")
                )
                qc_list = [int(each) for each in qc]
                df = pd.DataFrame(
                    {"time": ds["time"], "maxU": maxU, "maxU_qc": qc_list}
                )
            else:
                raise Warning(
                    "Dataset has more than one dimension and no exception for parquet."
                )
                return
        else:
            df = ds.to_dataframe(self.parameters.dim_order)  # type: ignore

        # Need to iterate through columns and force data types
        for col in df.columns:
            if "time" in col:
                continue
            elif "qc" in col:
                df[col] = pd.to_numeric(df[col])
            # else:
            # df[col] = df[col].astype(float)

        # print(df)
        df.to_parquet(filepath, **self.parameters.to_parquet_kwargs)
