# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 14:35:39 2022

@author: crisg
"""
import pandas as pd
import numpy as np
import re
import os

wrf_dir = r"D:\Cris Gino Mesias - User\Documents\MS_Meteo\Meteo_234_(Numerical_Weather_Prediction)\Lab_01\WRF_Output_Files"
coords_index = r"D:\Cris Gino Mesias - User\Documents\MS_Meteo\Meteo_234_(Numerical_Weather_Prediction)\Lab_01\WRF_Coords_Index.csv"
ogimet_root = r"D:\Cris Gino Mesias - User\Documents\MS_Meteo\Meteo_234_(Numerical_Weather_Prediction)\Lab_01\Ogimet_Data"
obs_root = r"D:\Cris Gino Mesias - User\Documents\MS_Meteo\Meteo_234_(Numerical_Weather_Prediction)\Lab_01\Observed_Data"

total = 0
coords_df = pd.read_csv(coords_index, index_col=False)
for i in coords_df.iterrows():
    station = i[1][0]
    station_no = i[1][0][0:5]
    
    station_dir = ogimet_root + "\\" + station + "\\"
    csv_filename = (os.listdir(station_dir))[0]
    full_path = station_dir + csv_filename
    
    ogimet_df = pd.read_csv(full_path, index_col=False)
    
    obs_temp = (ogimet_df['Temperature'] + 273.15).tolist()
    obs_press = (ogimet_df['Pressure']).tolist()
    
    #Null Masking
    null_rain = ogimet_df['Precipitation'] == '----'
    trace_rain = ogimet_df['Precipitation'].str[:2] == 'Tr'
    ogimet_df.loc[null_rain, 'Precipitation'] = '0.0/24h'
    ogimet_df.loc[trace_rain, 'Precipitation'] = '0.0/24h'
    
    #24h Rainfall Data Check
    prec_24h = ~((ogimet_df['Precipitation'].str.extract(r'(.*/[2][4]h)')).isna())
    mask_24h = prec_24h.squeeze()
    
    counter = 0
    for j in range(len(mask_24h)):
        if mask_24h.loc[j]:
            ext_rain_raw = (re.findall('.*\.\d{1}', (ogimet_df.loc[j, 'Precipitation'])))
            ext_rain_float = float(ext_rain_raw[0])
            ogimet_df.loc[j, 'Precipitation'] = ext_rain_float
            counter += 1
    
    obs_rain = ogimet_df['Precipitation'].tolist()
    
    temp_filename = station_no + "_" + "dtemp_s01_obs.npy"
    press_filename = station_no + "_" + "dpress_s01_obs.npy"
    rain_filename = station_no + "_" + "drain_obs.npy"
    
    base_dir = obs_root + "\\" + station + "\\"
    
    np.save(base_dir+temp_filename, obs_temp)
    np.save(base_dir+press_filename, obs_press)
    np.save(base_dir+rain_filename, obs_rain)
    
    total = total + counter