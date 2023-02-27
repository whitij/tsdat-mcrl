from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import pandas as pd
import csv
from tsdat import DataReader


class METReader(DataReader):
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

        f = open(input_key, "r")
        reader = csv.reader(f, delimiter=" ")

        for i, row in enumerate(reader):
            time = row[0] + " " + row[1]
            titles = row[1:][1::2]
            values = [float(x) for x in row[1:][2::2]]
            if i == 0:
                dicts = {}
                for j, key in enumerate(titles):
                    dicts[key] = list((values[j],))
                dicts["time"] = list((time,))  # type: ignore
            else:
                for j, key in enumerate(titles):
                    dicts[key].append(values[j])
                dicts["time"].append(time)  # type: ignore

        f.close()
        df = pd.DataFrame.from_dict(dicts)

        return df.to_xarray()
