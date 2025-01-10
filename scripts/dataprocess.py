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
    print("Usage: python scripts/dataprocess.py pollutant extent")
    sys.exit(1)

pollutant = sys.argv[1]
extent = sys.argv[2]
freq = 'monthly'
# if extent.lower() == 'extent':
#     csvs_path = os.getcwd()+'/data/'+pollutant+'_csvs/'
#     airsheds = ['INDIA']
# else:
#     csvs_path = os.getcwd()+'/data/'+pollutant+'_csvs/'
#     airsheds = glob.glob(os.getcwd()+"/data/gridextents_shponly/*.shp")

airsheds = [extent]
print(airsheds)
avogadro_constant = 6.022e23

date_pattern = r"(\d{4}-\d{2}-\d{2})"

for airshed in tqdm(airsheds):
    # if All_India_or_City.lower() == 'india':
    #     airshed_name = airshed
    # elif All_India_or_City.lower() == 'ea':
    #     airshed_name = airshed
    # else:
    #     airshed_name = airshed.split('/')[-1].split('.')[0][6:]

    csvs_path = os.getcwd()+'/data/{}_{}_{}_tifs/'.format(airshed, pollutant, freq)

    airshed_name = airshed

    csvs = glob.glob(csvs_path+airshed_name+'*.csv')
    csvs = natsorted(csvs)

    mean_pollutant_values = []
    dfs = []
    for csv in csvs:
        df = pd.read_csv(csv)
        date = re.findall(date_pattern, csv)[0]
        df['date'] = date
        dfs.append(df)

    df = pd.concat(dfs)
    print(df.head())
    df = df[['date','mean']]
    #df = df[['airshednum', 'airshednam', 'date', 'ISO_A3','mean']]
    print(df.shape)

    # Converting Mean Concentration from mol/m2 to molecules/m2
    if pollutant == "AOD":
        df['mean'] = 0.001*df['mean'] 

    TIME_SERIES_PATH = os.getcwd()+'/data/timeseries/'
    if not os.path.exists(TIME_SERIES_PATH[:-1]):
        os.makedirs(TIME_SERIES_PATH[:-1])
    df.to_csv(TIME_SERIES_PATH+'{}_{}_{}.csv'.format(airshed_name, pollutant, freq), index=False)
