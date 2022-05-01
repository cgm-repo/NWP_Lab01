import pandas as pd
import numpy as np
import os
from datetime import datetime

class Observation:
    def  __init__(self, input_prompt=True, path=""):
        if input_prompt:
            self.path = (input("Enter observation .csv file full path: ")).strip('"')
        else:
            self.path = path

        self.df = pd.read_csv(self.path, index_col=False)

    def isolate_var(self, variable, duration):
        df = self.df
        drop_list = []
        for idx, row in enumerate(df.itertuples(index=False)):
            date = datetime.strptime(row[0], '%m/%d/%Y %H:%M')
            if duration == 24 or duration == 0:
                duration = 0
                if date.hour != 0:
                    drop_list.append(idx)
            else:
                if date.hour % duration != 0:
                    drop_list.append(idx)

        df_conv = df.drop(drop_list)
        df_return = df_conv[variable]

        if variable == 'Precip':
            if duration == 0:
                check_df = df_conv['Precip_Dur'] == 24

                if check_df.eq(True).all():
                    df_return = df_conv['Precip']
                else:
                    df_return = df_conv[['Precip', 'Precip_Dur']]

        return df_return

    def var_save(self, var_df, filename):
        df_tosave = var_df.tolist()
        np.save(filename, df_tosave)

def synop_data(coords_path, ogimet_root, obs_root, duration, variables):
    coords_df = pd.read_csv(coords_path, index_col=False)
    for i in coords_df.iterrows():
        station = i[1][0]
        station_no = i[1][0][0:5]
        
        station_dir = ogimet_root + "\\" + station + "\\"
        csv_filename = (os.listdir(station_dir))[0]
        full_path = station_dir + csv_filename
        
        ogimet_df = Observation(input_prompt=False, path=full_path)

        base_dir = obs_root + "\\" + station + "\\"
        for j in range(len(variables)):
            var_name = variables[j]
            var_filename = '{0}{1}_{2}.npy'.format(base_dir, station_no, var_name)
            var_df = ogimet_df.isolate_var(var_name, duration)
            if variables[j] == 'Temp':
                temp_var = var_df + 273.15
                ogimet_df.var_save(temp_var, var_filename)
            else:
                ogimet_df.var_save(var_df, var_filename)
            
#Test
coords_path = r'D:\...\...\*.csv'
ogimet_root = r'D:\...\...\...'
obs_root = r'D:\...\...\...'
variables = ['Temp', 'Precip', 'SLP']

if __name__ == "__main__":
    synop_data(coords_path, ogimet_root, obs_root, 24, variables)