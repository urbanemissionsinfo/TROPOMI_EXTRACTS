import pandas as pd
import os
import glob
from natsort import natsorted
import re
import numpy as np
from tqdm import tqdm
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/dataprocess.py pollutant INDIA_OR_AIRSHED")
    sys.exit(1)

pollutant = sys.argv[1]
All_India_or_City = sys.argv[2]
if All_India_or_City.lower() == 'india':
    csvs_path = os.getcwd()+'/data/AllIndia_'+pollutant+'_csvs/'
    airsheds = ['INDIA']
else:
    csvs_path = os.getcwd()+'/data/'+pollutant+'_csvs/'
    airsheds = glob.glob(os.getcwd()+"/data/gridextents_shponly/*.shp")



avogadro_constant = 6.022e23

date_pattern = r"(\d{4}-\d{2}-\d{2})"

for airshed in tqdm(airsheds):
    if All_India_or_City.lower() == 'india':
        airshed_name = airshed
    else:
        airshed_name = airshed.split('/')[-1].split('.')[0][6:]
    
    csvs = glob.glob(csvs_path+airshed_name+'*.csv')
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

    # Converting Mean Concentration from mol/m2 to molecules/m2
    df['mean_concentration'] = avogadro_constant*df['mean_concentration'] 
    df.to_csv(os.getcwd()+'/data/timeseries/satellite_tropomi_{}_{}.csv'.format(pollutant.lower(), airshed_name.lower()), index=False)
