import pandas as pd
from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES
import numpy as np
import re
import os

class WRF:
    def __init__(self, input_prompt=True, path=""):
        if input_prompt:
            self.path = (input("Enter WRF .nc file full path: ")).strip('"')
        else:
            self.path = path

        wrf_df = Dataset(self.path, mode='r')

        self.lon = wrf_df.variables['XLONG'][:]
        self.lat = wrf_df.variables['XLAT'][:]
        self.time = wrf_df.variables['XTIME'][:]

        self.temp = getvar(wrf_df, "temp", units='K', meta=False, timeidx=ALL_TIMES)
        self.slp = getvar(wrf_df, "slp", meta=False, timeidx=ALL_TIMES)
        self.rain = wrf_df.variables['RAINC'][:] + wrf_df.variables['RAINNC'][:]
        self.olr = wrf_df.variables['OLR'][:]


    def read_lonlat(self):
        wrf_df = Dataset(self.path, mode='r')

        #Extracting WRF Model Longitude/Latitude
        lon_r = wrf_df.variables['XLONG'][:]
        lon = lon_r[0,0]

        lat_r = wrf_df.variables['XLAT'][:]
        lat = lat_r[0,:,0]

        return lon, lat

    def sum2inc(self, sum_var, hour_inc):
        minute_val = hour_inc * 60
        step_index = ((np.where((self.time % minute_val) == 0))[0]).tolist()

        base_shape = (sum_var).shape
        step_shape = (len(step_index), base_shape[1], base_shape[2])

        step_var = np.empty(shape=step_shape)

        prev_step_index = 0
        for step in range(len(step_index)):
            if step > 0:
                step_var[step,:,:] = (sum_var)[step_index[step],:,:] - (sum_var)[prev_step_index,:,:]
            prev_step_index = step_index[step]

        return step_var

def batch_npy_export(variable, filename, input_prompt=True, indices_path="", save_path=""):
    if input_prompt:
        indices_path = (input("Enter *.csv index file full path: ")).strip('"')
        save_path = (input("Enter full path to where to save output: ")).strip('"')

    indices_df = pd.read_csv(indices_path, index_col=False)

    for i in indices_df.iterrows():
        station = i[1][0]
        station_no = i[1][0][0:5]
        lon_index = i[1][1]
        lat_index = i[1][2]

        var_list = np.empty(shape=(0))
        var_list = np.append(var_list, variable[:,lat_index,lon_index])
        var_filename = station_no + filename

        base_dir = save_path + '\\' + station + '\\'
        np.save(base_dir+var_filename, var_list)


#Test
wrf_dir = r"D:\...\...\..."

counter = 0
for dirs in os.walk(wrf_dir):
    wrf_list = dirs[2]

var_list = ['PRESS', 'TEMP', 'RAIN']
attr_list = ['slp', 'temp', 'rain']
for i in range(len(var_list)):
    for output_file in wrf_list:
        wrf_filename = wrf_dir + "\\" + output_file
        base_name = (re.findall('mp[0-9][0-9]cu[0-9][0-9]', output_file))[0]
        wrf_df = WRF(input_prompt=False, path=wrf_filename)
        
        filename = "_" + base_name + "_" + var_list[i] + ".npy"
        vars()[var_list[i]] = getattr(wrf_df, attr_list[i])

        if var_list[i] == 'RAIN':
            vars()[var_list[i]] = wrf_df.sum2inc(vars()[var_list[i]], 24)
        
        batch_npy_export(vars()[var_list[i]], filename, input_prompt=False,
                         indices_path=r"D:\...\...\*.csv",
                         save_path=r"D:\...\...\...")

    