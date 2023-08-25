import pandas as pd
import os
import glob
from natsort import natsorted
import re
import numpy as np
from tqdm import tqdm

pollutant = 'SO2'
airsheds = glob.glob(os.getcwd()+"/data/gridextents_shponly/*.shp")
date_pattern = r"(\d{4}-\d{2}-\d{2})"

for airshed in tqdm(airsheds):
    airshed_name = airshed.split('/')[-1].split('.')[0][6:]
    
    csvs = glob.glob(os.getcwd()+'/data/'+pollutant+'_csvs/'+airshed_name+'*.csv')
    csvs = natsorted(csvs)

    mean_pollutant_values = []
    dates = []
    for csv in csvs:
        df = pd.read_csv(csv)
        try:
            mean_pollutant_value = df['mean'][0]
        except:
             mean_pollutant_value = np.nan
        mean_pollutant_values.append(mean_pollutant_value)
        date = re.findall(date_pattern, csv)[0]
        dates.append(date)
        
    df = pd.DataFrame([dates,mean_pollutant_values]).T
    df.columns=['date','mean_concentration']
    df.to_csv(os.getcwd()+'/data/timeseries/'+airshed_name+'_'+pollutant+'_timeseries.csv', index=False)
