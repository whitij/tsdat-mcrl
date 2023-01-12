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
            dataset.assign_coords(time=dt)

        # Note: the CTD calculates salinity onboard, so we don't need this conversion anymore
        """
        # equations from: https://salinometry.com/pss-78/
        # inputs: conductivity [mS/m], temperature [degC]
        # output: practical salinity, S [psu]
        # constants as defined by the Practical Salinity Scale - 1978 (PSS-78)
        a0 = 0.0080
        a1 = -0.1692
        a2 = 25.3851
        a3 = 14.0941
        a4 = -7.0261

        b0 = 0.0005
        b1 = -0.0056
        b2 = -0.0066
        b3 = -0.0375
        b4 = 0.0636
        b5 = -0.0144

        C0 = 0.6766097
        C1 = 2.00564e-2
        C2 = 1.104259e-4
        C3 = -6.9698e-7
        C4 = 1.0031e-9

        k = 0.0162
        t = dataset["temp"]

        # The conductivity ratio, R, is the conductivity input from the sensor divided by the present estimate
        # C(35,15_68,0) = 42.914 mS/cm = 4.2914 S/m
        C = 4291.4  # mS/m
        R = dataset["conductivity"] / C
        r_T = C0 + C1 * t + C2 * t**2 + C3 * t**3 + C4 * t**4
        R_t = R / r_T

        S = (
            a0
            + a1 * R_t ** (1 / 2)
            + a2 * R_t
            + a3 * R_t ** (3 / 2)
            + a4 * R_t**2
            + a3 * R_t ** (5 / 2)
            + (
                (t - 15)
                / (1 + k * (t - 15))
                * (
                    b0
                    + b1 * R_t ** (1 / 2)
                    + b2 * R_t
                    + b3 * R_t ** (3 / 2)
                    + b4 * R_t**2
                    + b5 * R_t ** (5 / 2)
                )
            )
        )
        dataset["salinity"] = S
        """
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        write_parquet(dataset, "ctd")

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
