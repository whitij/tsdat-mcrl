from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
import csv
from tsdat import DataReader


class TideGaugeReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        """If your CustomDataReader should take any additional arguments from the
        retriever configuration file, then those should be specified here.

        e.g.,:
        custom_parameter: float = 5.0

        """

    parameters: Parameters = Parameters()
    """Extra parameters that can be set via the retrieval configuration file. If you opt
    to not use any configuration parameters then please remove the code above."""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(
            input_key,
            sep=",| ",
            header=None,
            engine="python",
            names=("date", "time", "ms", "flag", "water_level"),
        )
        df["time"] = df["date"] + " " + df["time"] + "." + [str(x) for x in df["ms"]]
        # The flag was removed in later versions, so copy if needed
        df["water_level"] = np.where(
            df["water_level"].isnull(), df["flag"], df["water_level"]
        )
        df = df.drop(columns=["date", "ms", "flag"])
        return df.to_xarray()
