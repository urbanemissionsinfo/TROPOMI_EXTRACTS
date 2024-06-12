import pandas as pd 
import glob
import os
import regex as re
from datetime import datetime
from natsort import natsorted

import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/extent_grids_composite.py extent pollutant")
    sys.exit(1)

extent = sys.argv[1].upper()
pollutant = sys.argv[2].upper()

csvs = glob.glob(os.getcwd() + '/data/{}_{}_regridded/regridded*.csv'.format(extent, pollutant))
composite_df = pd.read_csv(csvs[0])[['Maille', 'Maille_Y', 'Maille_X']]

for csv in tqdm(natsorted(csvs)):
    df = pd.read_csv(csv)[['value']]
    month = re.findall(r"\d{4}\-\d{2}", csv)[0]
    parsed_date = datetime.strptime(month, "%Y-%m")
    formatted_date = parsed_date.strftime("%Y%b").upper() #2019JAN, ...

    composite_df[formatted_date] = df.value

composite_folder_path = os.getcwd() + '/data/{}_composites/'.format(extent)
if not os.path.exists(composite_folder_path[:-1]):
        os.makedirs(composite_folder_path[:-1])

composite_df.to_csv(composite_folder_path + '{}_composite_{}.csv'.format(extent, pollutant), index=False)