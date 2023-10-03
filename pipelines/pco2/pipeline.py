import xarray as xr

from tsdat import IngestPipeline
from shared.writers import write_parquet


class PCO2(IngestPipeline):
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        air_positions = [s for s in dataset["position"].values if "Air" in s]

        # Set air samples from full variable saved in water variable
        dataset["pco2_air"].loc[dict(position=air_positions)] = dataset[
            "pco2_water"
        ].sel(position=air_positions)
        dataset["o2_air"].loc[dict(position=air_positions)] = dataset["o2_water"].sel(
            position=air_positions
        )

        # Remove air samples from water sample variable
        dataset["pco2_water"].loc[dict(position=air_positions)] = -9999
        dataset["o2_water"].loc[dict(position=air_positions)] = -9999

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
