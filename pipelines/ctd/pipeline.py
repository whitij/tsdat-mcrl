import numpy as np
import pandas as pd
import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class CTD(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        # This used to be in local time, changed to UTC on 2023-1-5 3:30pm (local time)
        if dataset.time[-1] < np.datetime64("2023-01-05T15:31:00"):
            dt = pd.to_datetime(dataset.time.data, format="%Y-%m-%d %H:%M:%S.%f")
            dt = dt.tz_localize("US/Pacific").tz_convert("UTC")  # type: ignore
            # Numpy can't handle localized datetime arrays so we force the datetime to
            # be naive (i.e. timezone 'unaware').
            dt = dt.tz_localize(None)  # type: ignore
            dataset = dataset.assign_coords(time=dt)

        # Note: the CTD calculates salinity onboard, so we don't need this conversion anymore
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Rename description to summary for CF compliance
        dataset.attrs["summary"] = dataset.attrs.pop("description")

        write_parquet(dataset, "ctd")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
