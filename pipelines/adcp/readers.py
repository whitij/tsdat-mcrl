from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import numpy as np

from tsdat import DataReader
from mhkit import dolfyn


class ADCPDataReader(DataReader):
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
        dat = dolfyn.read(input_key)

        # Most instruments record pressure data, but not all record the water salinity
        dolfyn.adp.clean.find_surface_from_P(dat, salinity=30)

        # Guestimate declination by current change of 0.1 deg W per year
        t = dolfyn.time.dt642date(dat.time)[0]
        day_of_year = t.timetuple().tm_yday
        declin = 15.66 - (t.year - 2022 + day_of_year / 365.25) * 0.1

        # hack for 2-beam ADCP to enable inst2earth rotations to add magnetic declination
        dat["vel"][2, ...] = np.zeros(
            dat["vel"].shape[-2:]
        )  # set vertical velocity to 0
        dat.velds.set_declination(round(declin, 2))

        # Set speed and direction
        dat["U_mag"] = dat.velds.U_mag
        dat["U_dir"] = dat.velds.U_dir

        # Convert from [0, 360] back to [-180, 180]
        u_dir = dat["U_dir"].values
        u_dir[u_dir > 180] -= 360
        dat["U_dir"].values = u_dir

        return dat
