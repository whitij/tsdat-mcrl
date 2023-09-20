from typing import Dict, Union
import numpy as np
import pandas as pd
import xarray as xr
from tsdat import DataReader


class ReadPCO2Logfile(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that reads pCO2 logfiles sent from the edge computer
    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        #ds = xr.Dataset(dims=['time', 'position'])
        position = ['Air_cycle_pump_on',  # air samples
                    'Air_cycle_pump_off',  
                    'Equil_cycle_pump_on',  # water samples
                    'Equil_cycle_pump_off']        
        
        df = pd.read_csv(input_key, header=0, sep=' ')
        data = dict.fromkeys(position)
        
        # Dump data into nested dictionary
        for i, row in enumerate(df['Time']):
            if 'operation_mode' in row.lower():
                pos = df['CO2[ppm]'][i]
                data[pos] = dict.fromkeys(df.columns.values)
            else:
                for var in df.columns:
                    if not data[pos][var]:
                        data[pos][var] = []
                    if var=='Time':
                        dat = np.datetime64(df[var][i])
                    else:
                        dat = float(df[var][i])
                    data[pos][var].append(dat)
        
        # Create 4 datasets for each "position"
        datasets = dict()
        for pos in data.keys():
            for var in data[pos].keys():
                data[pos][var] = {"dims": ("Time"), "data": data[pos][var]}
        
            datasets[pos] = xr.Dataset.from_dict(data[pos])

        # Combine into 1 dataset
        n_samples = datasets[position[0]]['Time'].size
        new_dict = {var: np.empty((4, n_samples)) for var in datasets[position[0]].data_vars}
        time_list = np.empty((4, n_samples))
        
        for i, pos in enumerate(position):
            for var in datasets[pos]:
                new_dict[var][i] = datasets[pos][var].values
            time_list[i] = datasets[pos]['Time'].values
        
        ds = xr.Dataset()
        ds['position'] = xr.DataArray(position, dims=['position'])
        # ds['sample'] = xr.DataArray(np.arange(0,n_samples), dims=['sample'])
        # ds['time'] = xr.DataArray(time_list.astype('datetime64[ns]').T, dims=['sample','position'])
        ds['time'] = xr.DataArray(time_list.mean(axis=0).astype('datetime64[ns]').T, dims=['time'])
        for var in datasets[pos]:
            # ds[var] = xr.DataArray(new_dict[var].T, dims=['sample', 'position'])
            ds[var] = xr.DataArray(new_dict[var].T, dims=['time', 'position'])
        
        return ds
