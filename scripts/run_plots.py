from datetime import date, timedelta
import subprocess
import os
import pandas as pd
import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 2:
    print("Usage: python scripts/run_plots.py <python_code>")
    sys.exit(1)

code_name = sys.argv[1]

if code_name not in ['timeseries_plot', 'season_plot']:
    print("Error: Code does not exist. Choose from: 'timeseries_plot', 'season_plot' ")
    sys.exit(2)

city_state_file_names = pd.read_csv(os.getcwd()+'/data/city_state_file_names.csv')
script_path = os.getcwd()+'/scripts/{}.py'.format(code_name)

for airshed in tqdm(city_state_file_names['filename']):
    for pollutant in ["NO2", "SO2", "HCHO", "O3"]:
        subprocess.call(['python', script_path, pollutant, airshed])