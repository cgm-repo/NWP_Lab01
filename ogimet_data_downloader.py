import requests
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def tonum(digit):
    try:
        f_digit = float(digit)
        return f_digit
    except:
        return None

def ogimetdatadl(stat_id, end_date, duration, root=""):
    date_info = datetime.strptime(end_date, '%Y/%m/%d')
    year = str(date_info.year)
    month = str(date_info.month)
    day = str(date_info.day)
    
    url = "https://ogimet.com/cgi-bin/gsynres?lang=en&ind={0}&decoded=yes&ndays={1}&ano={2}&mes={3}&day={4}&hora=00".format(str(stat_id), str(duration), year, month, day)
    
    response = requests.get(url)
    src = response.content
    soup = BeautifulSoup(src, 'html.parser')
    
    tables = soup.find_all("table")
    
    df = list(pd.read_html(str(tables[2]))[0])
    
    output_table = pd.DataFrame(columns=['DateTime', 'Pressure', 'Temperature', 'Precipitation'])
    
    press_index = 8
    temp_index = 2
    precip_index = 9
    
    for entry in range(len(df)):
        if df[entry][0] ==  'T(C)':
            temp_index = entry
        if df[entry][0] ==  'P0hPa':
            press_index = entry
        if df[entry][0] ==  'Prec(mm)':
            precip_index = entry
    
    for i in  range((len(df[0]) - 1), 0, -1):
        datetime_text = df[0][i] + " " + df[1][i]
        datetime_input =  datetime.strptime(datetime_text, '%d/%m/%Y %H:%M')
        press_input = tonum(df[press_index][i])
        temp_input = tonum(df[temp_index][i])
        precip_input = df[precip_index][i]
        
        #At observation times (uncomment as needed)
        
        temp_df = pd.DataFrame({'DateTime': [str(datetime_input)],
                                'Pressure': [press_input],
                                'Temperature': [temp_input],
                                'Precipitation': [precip_input]})
        
        output_table = output_table.append(temp_df, ignore_index=True)
        
        #At 0000 UTC
        """
        if datetime_input.hour == 0:
            temp_df = pd.DataFrame({'DateTime': [str(datetime_input)],
                                    'Pressure': [press_input],
                                    'Temperature': [temp_input],
                                    'Precipitation': [precip_input]})
            
            output_table = output_table.append(temp_df, ignore_index=True)"""
    
    filename = "{0}_Obs_Data_{1}{2}{3}n{4}.csv".format(stat_id, year, month, day, duration)
    csv_dir = root + filename
    output_table.to_csv(csv_dir, index=False)
    
    # Observation Data Check
    missing_data = False
    if (output_table['Pressure'].count() < len(output_table)) or \
       (output_table['Temperature'].count() < len(output_table)) or \
       (output_table['Precipitation'].count() < len(output_table)):
        missing_data = True
        return missing_data

if __name__ == "__main__":
    stat_id = 98444
    end_date = '2021/02/05'
    duration = 4
    a = ogimetdatadl(stat_id, end_date, duration)