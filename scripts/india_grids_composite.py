import pandas as pd 
import glob
import os
import regex as re
from datetime import datetime
from natsort import natsorted

import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 2:
    print("Usage: python scripts/india_grids_composite.py pollutant")
    sys.exit(1)

pollutant = sys.argv[1].upper()

csvs = glob.glob(os.getcwd() + '/data/AllIndia_{}_regridded/regridded*.csv'.format(pollutant))
composite_df = pd.read_csv(csvs[0])[['Maille', 'Maille_Y', 'Maille_X']]

for csv in tqdm(natsorted(csvs)):
    df = pd.read_csv(csv)[['value']]
    month = re.findall(r"\d{4}\-\d{2}", csv)[0]
    parsed_date = datetime.strptime(month, "%Y-%m")
    formatted_date = parsed_date.strftime("%Y%b").upper() #2019JAN, ...

    composite_df[formatted_date] = df.value

composite_df.to_csv(os.getcwd() + '/data/AllIndia_{}_regridded/INDIA_composite_{}.csv'.format(pollutant,pollutant), index=False)