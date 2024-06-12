import os
import glob
import geopandas as gpd 
import rasterio
import numpy as np
import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 2:
    print("Usage: python scripts/rename.py pollutant")
    sys.exit(1)

pollutant = sys.argv[1].upper()

path = os.getcwd() + '/data/EastAfrica_{}_tifs/'.format(pollutant)
grids = gpd.read_file(os.getcwd() + '/assets/grids_ea/grids_eastafrica.shp')

tifs = glob.glob(path+"/*.tif")

def remove_spaces_from_filenames(tifs):
    for tif in tifs:
        if ' ' in tif:
            new_file = tif.replace(' ', '')  # Replace space with underscore
            os.rename(tif, new_file)
        else:
            print(f'No spaces in')

# Call the function
remove_spaces_from_filenames(tifs)
