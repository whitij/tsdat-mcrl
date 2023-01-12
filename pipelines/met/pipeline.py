import numpy as np
import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class MET(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        # This used to be in local daylight time, changed to UTC on 2023-1-5 3:08pm (local time)
        if dataset.time[-1] < np.datetime64("2023-01-05T16:11:00"):
            # Always add 7 hours instead of using timezone conversion because it was stuck in PDT
            newTime = dataset.time + np.timedelta64(7, "h")
            dataset.assign_coords(time=newTime)

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        write_parquet(dataset, "met")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
