import requests
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import numpy as np

#Complete SYNOP variables
VAR_LIST = ['Date', 'T(C)', 'Td(C)', 'Hr%',
            'Tmax(C)', 'Tmin(C)', 'ddd', 'ffkmh',
            'P0hPa', 'P seahPa', 'PTnd', 'Prec(mm)',
            'Nt', 'Nh', 'HKm', 'Viskm']

VAR_PROP = ['Date', 'Temp', 'Dew_Pt', 'RH',
            'Max_Temp', 'Min_Temp', 'Wind_Dir', 'Wind_Speed',
            'Base_Press', 'SLP', 'Press_Trend', 'Precip',
            'Total_Cover', 'Low_Cover', 'Cloud_Base', 'Vis']

class Ogimet_Entry:
    def __init__(self, stat_id, start_date, end_date):
        self.stat_id = str(stat_id)
        self.start_date = datetime.strptime(start_date, '%Y/%m/%d')
        self.end_date = datetime.strptime(end_date, '%Y/%m/%d')
        self.duration = str((self.end_date - self.start_date).days)

def ogimetdatadl(stat_id, start_date, end_date, root=""):
    date_info = Ogimet_Entry(stat_id, start_date, end_date)
    year = str(date_info.end_date.year)
    month = str(date_info.end_date.month)
    day = str(date_info.end_date.day)
    
    url = "https://ogimet.com/cgi-bin/gsynres?lang=en&ind={0}&decoded=yes&ndays={1}&ano={2}&mes={3}&day={4}&hora=00".format(date_info.stat_id, date_info.duration, year, month, day)
    
    response = requests.get(url)
    src = response.content
    soup = BeautifulSoup(src, 'html.parser')
    
    tables = soup.find_all("table")
    
    df_raw = pd.read_html(str(tables[2]))
    df = df_raw[0]
    
    column_list = []
    for variable in VAR_LIST:
        try:
            (list(df[variable]))[0]
            column_list.append(variable)
        except KeyError:
            continue

    output_table = pd.DataFrame(columns=[])

    for col_index in range(len(column_list)):
        if col_index == 0:
            date_span = np.asarray((list(df['Date']))[0])
            time_span = np.asarray((list(df['Date']))[1])
            arr_list = [date_span, time_span]
            date_arr = np.apply_along_axis(' '.join, 0, arr_list)
            output_table = output_table.assign(Date=date_arr)
        
        #col_index=1 has the same name as col_index=0
        else:
            col_var = column_list[col_index]
            col_name = VAR_PROP[col_index]
            col_value = np.asarray((list(df[col_var]))[0])
            null_val = np.where((np.char.endswith(col_value, '-')) == True)
            col_value[null_val] = 999999

            output_table.insert(col_index, col_name, col_value)

            if column_list[col_index] == 'Prec(mm)':
                rain_raw = np.char.split(col_value, sep='/')
                rain_shape = rain_raw.shape
                rain_val = np.empty(shape=rain_shape)
                rain_dur = np.empty(shape=rain_shape)
                
                for i in range(rain_shape[0]):
                    if rain_raw[i][0] != '999999':
                        if rain_raw[i][0] == 'Tr':
                            rain_val[i] = 0
                            rain_dur[i] = 0
                        else:
                            rain_val[i] = rain_raw[i][0]
                            rain_dur[i] = (rain_raw[i][1]).strip("h") 
                    else:
                        rain_val[i] = 999999
                        rain_dur[i] = 0
                
                output_table['Precip'] = rain_val
                output_table.insert(col_index, 'Precip_Dur', rain_dur)
  
    filename = "{0}_Obs_Data_{1}-{2}.csv".format(date_info.stat_id, date_info.start_date.strftime('%Y%m%d'), date_info.end_date.strftime('%Y%m%d'))
    csv_dir = root + filename
    output_table.to_csv(csv_dir, index=False)

    return output_table

#Ogimet Downloader Test
if __name__ == "__main__":
    stat_id = 98444
    start_date = '2014/07/13'
    end_date = '2014/07/16'

    ##Console Input
    #stat_id = input("Enter WMO Index: ")
    #start_date = input("Enter start date (yyyy/mm/dd): ")
    #end_date = input("Enter end date (yyyy/mm/dd): ")

    a = ogimetdatadl(stat_id, start_date, end_date)