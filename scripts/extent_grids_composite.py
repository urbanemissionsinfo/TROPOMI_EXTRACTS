import pandas as pd 
import glob
import os
import regex as re
from datetime import datetime
from natsort import natsorted

import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 4:
    print("Usage: python scripts/extent_grids_composite.py extent pollutant freq")
    sys.exit(1)

extent = sys.argv[1].upper()
pollutant = sys.argv[2].upper()
freq = sys.argv[3].lower() #monthly/weekly/yearly

csvs = glob.glob(os.getcwd() + '/data/{}_{}_regridded_{}/regridded*.csv'.format(extent, pollutant, freq))
composite_df = pd.read_csv(csvs[0])[['Maille', 'Maille_Y', 'Maille_X']]

for csv in tqdm(natsorted(csvs)):
    df = pd.read_csv(csv)[['value']]
    if pollutant=="AOD":
         df.value = 0.001*df.value

    month = re.findall(r"\d{4}\-\d{2}", csv)[0]
    parsed_date = datetime.strptime(month, "%Y-%m")
    if freq == 'monthly':
        formatted_date = parsed_date.strftime("%Y%b").upper() #2019JAN, ...
    elif freq == 'yearly':
        formatted_date = parsed_date.strftime("%Y").upper() #2019, ...
    else:
        print("Check frequency")
        sys.exit(1)

    composite_df[formatted_date] = df.value

composite_folder_path = os.getcwd() + '/data/{}_composites/'.format(extent)
if not os.path.exists(composite_folder_path[:-1]):
        os.makedirs(composite_folder_path[:-1])

composite_df.to_csv(composite_folder_path + '{}_composite_{}_{}.csv'.format(extent, pollutant, freq), index=False)