import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from matplotlib.ticker import ScalarFormatter

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/timeseries_plot.py pollutant airshed")
    sys.exit(1)

pollutant = sys.argv[1]
airshed = sys.argv[2]

if pollutant.lower() == 'no2':
    plot_color = 'blue'
elif pollutant.lower() == 'so2':
    plot_color = 'red'
elif pollutant.lower() == 'o3':
    plot_color = 'purple'
elif pollutant.lower() == 'hcho':
    plot_color = 'green'
else:
    print("Please check. Invalid name of airshed or pollutant: ", airshed)
    sys.exit(2)

# Create a DataFrame with date and values
try:
    df = pd.read_csv(os.getcwd() + '/data/timeseries/satellite_tropomi_{}_{}.csv'.format(pollutant.lower(), airshed.lower()))
    df['date'] = pd.to_datetime(df['date'])
except:
    print("Please check. Invalid name of airshed or pollutant: ", airshed)
    sys.exit(2)

# Take city name from city_state_file_names.csv for Plot title
city_state_file_names = pd.read_csv(os.getcwd()+'/data/city_state_file_names.csv')
if airshed.lower() == 'india':
    airshed_on_plot = 'INDIA'
    # Add data source annotation
    data_source_annotation = '''Monthly averages of India airshed covering grids of 0.1 degree resolution
    Data is extracted using Google Earth Engine algorithms'''

else:
    airshed_on_plot = city_state_file_names[city_state_file_names['filename'] == airshed.lower()]['citystatename'].to_list()[0]
    airshedsize = city_state_file_names[city_state_file_names['filename'] == airshed.lower()]['airshedsize'].to_list()[0]
    # Add data source annotation
    data_source_annotation = '''15-day averages of city airshed covering {} grids of 0.01 degree resolution
    Data is extracted using Google Earth Engine algorithms'''.format(airshedsize)


# Plot the time series
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['mean_concentration'], marker='o', linestyle='-', color = plot_color)

plt.title('Mean TROPOMI Columnar Density of {} for {}'.format(pollutant, airshed_on_plot))
plt.xlabel('Date')
plt.ylabel('Unit: molecules/$m^2$ * $10^{20}$')

# Customize grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)  # Enable grid for both major and minor ticks


# Customize grid for quarters
quarter_dates = pd.date_range(start=df['date'].to_list()[0], end=df['date'].to_list()[-1], freq='Q')
for q_date in quarter_dates:
    plt.axvline(x=q_date, color='lightgray', linestyle='--', linewidth=0.5)

# Customize grid for years
year_dates = pd.date_range(start=df['date'].to_list()[0] - timedelta(days=1),
                           end=df['date'].to_list()[-1] + timedelta(days=30),
                           freq='Y')
for y_date in year_dates:
    plt.axvline(x=y_date, color='gray', linestyle='-', linewidth=0.5)

plt.text(0.01, 0.02, data_source_annotation, fontsize=7, color='gray', transform=plt.gcf().transFigure)

# Load the image
logo = plt.imread(os.getcwd() + '/assets/logo.grid.3_transp.png')  # Provide the path to your image file
plt.figimage(logo, xo=900, yo=0.02)

# Set the y-axis formatter to use scientific notation with exponent 1e20
formatter = ScalarFormatter(useMathText=True)
formatter.set_powerlimits((20, 20))  # Set the exponent to 1e20
plt.gca().yaxis.set_major_formatter(formatter)

plt.tight_layout()
plt.savefig(os.getcwd() + '/plots/satellite_tropomi_timeseries/satellite_tropomi_{}_{}.png'.format(pollutant.lower(), airshed.lower()))