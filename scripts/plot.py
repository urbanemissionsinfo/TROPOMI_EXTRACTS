import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/plot.py pollutant airshed")
    sys.exit(1)

pollutant = sys.argv[1]
airshed = sys.argv[2]

# Create a DataFrame with date and values
try:
    df = pd.read_csv(os.getcwd() + '/data/timeseries/{}_{}_timeseries.csv'.format(airshed, pollutant))
    df['date'] = pd.to_datetime(df['date'])
except:
    print("Please check. Invalid name of airshed or pollutant")
    sys.exit(2)


# Plot the time series
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['mean_concentration'], marker='o', linestyle='-')
plt.title('Mean Concentration of {} for {}'.format(pollutant, airshed))
plt.xlabel('Date')
plt.ylabel('Concentration')
plt.grid(True)
plt.savefig(os.getcwd() + '/plots/{}_{}_timeseries.jpg'.format(airshed,pollutant))
print("Plot saved in plots folder")