import numpy as np
import pandas as pd
import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class Tide_Gauge(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        # Water level in NAVD88: 3.713m - offset - value
        # The offset is 0.0561266 meters, as measured by Nolann Williams (9/2021)
        dataset["water_level"].data = 3.713 - 0.0561266 - dataset["water_level"].data

        # This used to be in local time, changed to UTC on 2023-1-5 3:30pm (local time)
        # Log files were always named in UTC, but the data was saved in Pacific
        if dataset.time[-1] < np.datetime64("2023-01-05T15:31:00"):
            dt = pd.to_datetime(dataset.time.data, format="%Y-%m-%d %H:%M:%S.%f")
            dt = dt.tz_localize("US/Pacific").tz_convert("UTC")  # type: ignore
            # Numpy can't handle localized datetime arrays so we force the datetime to
            # be naive (i.e. timezone 'unaware').
            dt = dt.tz_localize(None)  # type: ignore
            dataset = dataset.assign_coords(time=dt)

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Example of how to change calibration date
        # if dataset[time][0] < datetime(2022,1,1)
        #  dataset.attrs[calibration_date] = '2017/01/01'

        # Rename description to summary for CF compliance
        dataset.attrs["summary"] = dataset.attrs.pop("description")

        write_parquet(dataset, "tide_gauge")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
