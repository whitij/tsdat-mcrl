import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class PCO2(IngestPipeline):
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        # Set air and water sample measurements from raw pCO2 and O2 data
        dataset["pco2_air"].values = (
            dataset["pco2_raw"].sel(position="Air cycle pump off").mean("sample")
        ).values
        dataset["pco2_water"].values = (
            dataset["pco2_raw"].sel(position="Equil cycle pump off").mean("sample")
        ).values

        dataset["o2_air"].values = (
            dataset["o2_raw"].sel(position="Air cycle pump off").mean("sample")
        ).values
        dataset["o2_water"].values = (
            dataset["o2_raw"].sel(position="Equil cycle pump off").mean("sample")
        ).values

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Rename description to summary for CF compliance
        dataset.attrs["summary"] = dataset.attrs.pop("description")

        write_parquet(dataset, "pco2")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
