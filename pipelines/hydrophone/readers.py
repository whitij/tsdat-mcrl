from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import numpy as np
import csv
from tsdat import DataReader


class HydrophoneReader(DataReader):
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
        # read text file
        dat = pd.read_csv(input_key, header=26, sep="\t")

        # extract frequency vector
        frequency = [int(x) for x in dat.columns.values.tolist()[6:]]

        # add date to time (from header)
        time = np.array(dat.Time)

        f = open(input_key, "r")
        reader = list(csv.reader(f, delimiter="\t"))
        date = reader[3][1]
        f.close()

        time = [date + " " + x for x in time]  # type: ignore

        # extract frequency data
        freqdata = dat[dat.columns.values.tolist()[6:]]

        dataset = xr.Dataset(
            data_vars=dict(
                spectra=(["time", "frequency"], freqdata),
                temperature=(["time"], dat["Temperature [C]"]),
                humidity=(["time"], dat["Humidity [%]"]),
                sequence=(["time"], dat["Sequence #"]),
            ),
            coords={"time": time, "frequency": frequency},
        )
        return dataset
