import pandas as pd
from netCDF4 import Dataset
import numpy as np

class Station:
    def __init__(self, stat_id, lon, lat):
        self.stat_id = str(stat_id)
        self.lon = lon
        self.lat = lat

    def geoindexer(self, wrf_lon, wrf_lat):
        lon_index = closest(wrf_lon, self.lon)[1]
        lat_index = closest(wrf_lat, self.lat)[1]

        self.lon_index = lon_index
        self.lat_index = lat_index

        return lon_index, lat_index

class WRF:
    def __init__(self, input_prompt=True, path=""):
        if input_prompt:
            self.path = (input("Enter WRF .nc file full path: ")).strip('"')
        else:
            self.path = path

    def read_lonlat(self):
        wrf_df = Dataset(self.path, mode='r')

        #Extracting WRF Model Longitude/Latitude
        lon_r = wrf_df.variables['XLONG'][:]
        lon = lon_r[0,0]

        lat_r = wrf_df.variables['XLAT'][:]
        lat = lat_r[0,:,0]

        return lon, lat

def closest(lst, K):
     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     return lst[idx], idx

def batch_geoindex(input_prompt=True, csv_save=True, coords_path="", wrf_path=""):
    if input_prompt:
        coords_path = (input("Enter .csv file full path: ")).strip('"')
        wrf_lon, wrf_lat = WRF().read_lonlat()
    else:
        coords_path = coords_path
        wrf_lon, wrf_lat = WRF(input_prompt=False, path=wrf_path).read_lonlat()

    coords_df = pd.read_csv(coords_path)

    stat_coords = pd.DataFrame(columns=['Station_ID', 'Lon_Index', 'Lat_Index'])
    for i in range(len(coords_df)):
        stat_ID = coords_df.loc[i].at['Station_ID']
        stat_lon = coords_df.loc[i].at['Lon']
        stat_lat = coords_df.loc[i].at['Lat']
        
        lon_index, lat_index = Station(stat_ID, stat_lon, stat_lat).geoindexer(wrf_lon, wrf_lat)
        
        temp_df = pd.DataFrame({'Station_ID': [stat_ID],
                                'Lon_Index': [lon_index],
                                'Lat_Index': [lat_index]})
        
        stat_coords = stat_coords.append(temp_df, ignore_index=True)

    if csv_save:
        stat_coords.to_csv('WRF_Coords_Index.csv', index=False)
    else:
        return stat_coords

#Test
if __name__ == "__main__":
    #Load WRF (Default)
    wrf_lon, wrf_lat = WRF().read_lonlat()
    
    #Load WRF (Input=False)
    wrf_lon, wrf_lat = WRF(input_prompt=False, path=r"D:\...\...\.nc").read_lonlat()
    
    #Geoindex for one SYNOP
    LGP = Station(98444, 123.733, 13.138)
    lon_index, lat_index = LGP.geoindexer(wrf_lon, wrf_lat)
    print(lon_index, lat_index)
    
    #Batch Geoindex (Default)
    batch_geoindex()
    
    #Batch Geoindex (Input=False)
    pd_coords = batch_geoindex(input_prompt=False, csv_save=False,
                               coords_path=r"D:\...\...\.csv",
                               wrf_path=r"D:\...\...\.nc")
    