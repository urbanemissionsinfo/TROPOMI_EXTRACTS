import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter
from datetime import datetime, timedelta

import os
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/plot.py pollutant airshed")
    sys.exit(1)

pollutant = sys.argv[1]
airshed = sys.argv[2]

# Take city name from city_state_file_names.csv for Plot title
city_state_file_names = pd.read_csv(os.getcwd()+'/data/city_state_file_names.csv')
airshed_on_plot = city_state_file_names[city_state_file_names['filename'] == airshed.lower()]['citystatename'].to_list()[0]
airshedsize = city_state_file_names[city_state_file_names['filename'] == airshed.lower()]['airshedsize'].to_list()[0]

# Create a DataFrame with date and values
try:
    df = pd.read_csv(os.getcwd() + '/data/timeseries/satellite_tropomi_{}_{}.csv'.format(pollutant.lower(), airshed.lower()))
    df['date'] = pd.to_datetime(df['date'])
except:
    print("Please check. Invalid name of airshed or pollutant")
    sys.exit(2)


df['year'] = df['date'].dt.year
df['date'] = df['date'].dt.strftime('%b-%d') #Remove year from timestamp

df_pivot = pd.pivot_table(df,
                          index=['date'],
                          columns='year',
                          values='mean_concentration').reset_index()



color_dict = {
              2019: '#808080',
              2020: '#ff0000',
              2021: '#4ea72e',
              2022: '#4e95d9',
              2023: '#215f9a',
              2024: '#3B3F44'
              }

df_pivot.set_index('date',inplace=True)

## SORT THE  DATETIME INDEX WHICH IS IN STRING FORMAT ##
# Convert the index to datetime
df_pivot.index = pd.to_datetime(df_pivot.index + '-2000', format='%b-%d-%Y')
# Sort the DataFrame by the datetime index
df_pivot = df_pivot.sort_index()
# Remove the year from the index
df_pivot.index = df_pivot.index.strftime('%b-%d')
df_pivot.plot(figsize=(16, 8),
        color=[color_dict.get(x) for x in df_pivot.columns],
        linewidth = 3)

plt.title('Mean TROPOMI Columnar Density of {} for {}'.format(pollutant, airshed_on_plot), fontsize=20)
plt.xlabel('Date', fontsize=15)
plt.ylabel('Unit: molecules/${m^2}$ * ${10^{20}}$', fontsize=17)
# Set the y-axis formatter to use scientific notation with exponent 1e19
formatter = ScalarFormatter(useMathText=True)
formatter.set_powerlimits((20, 20))  # Set the exponent to 1e20
plt.gca().yaxis.set_major_formatter(formatter)
plt.yticks(fontweight='bold', fontsize=10)

# Add data source annotation
data_source = '''15-day averages of city airshed covering {} grids of 0.01 degree resolution
Data is extracted using Google Earth Engine algorithms'''.format(airshedsize)
plt.text(0.01, 0.02, data_source, fontsize=8, color='gray', transform=plt.gcf().transFigure)

# Load the image
logo = plt.imread(os.getcwd() + '/assets/logo.grid.3_transp.png')  # Provide the path to your image file
plt.figimage(logo, xo=1500, yo=0.02)

# Customize grid
plt.xticks(np.arange(0, 23, 2),
           [month[:3] for month in df_pivot.index[0::2].to_list()],
           fontweight='bold', fontsize=10)  # Adjust the range and step size as needed
plt.grid(True, color='gray')  # Enable grid for both major and minor ticks

plt.legend(loc='lower center', ncol=len(df_pivot.columns), fontsize=10.5)
plt.tight_layout()
plt.savefig(os.getcwd() + '/plots/satellite_tropomi_season/satellite_tropomi_season_{}_{}.png'.format(pollutant.lower(), airshed.lower()))
