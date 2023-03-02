import numpy as np
import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class Hydrophone(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        f1 = 0  # bottom of frequency band [ Hz]
        f2 = 250000  # top of frequency band [Hz]
        f = dataset["frequency"]
        p = 10 ** (
            (dataset["spectra"] + 87) / 20
        )  # convert to dB re 1 uPa using offset, then to uPa
        (f_keep,) = np.where((f <= f2) & (f >= f1))  # trim to frequency band
        p = p[:, f_keep]
        SPL = 10 * np.log10(np.trapz(p, f, axis=1))  # calculate SPL
        dataset["SPL"].data = SPL
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Rename description to summary for CF compliance
        dataset.attrs["summary"] = dataset.attrs.pop("description")

        write_parquet(dataset, "hydrophone")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
