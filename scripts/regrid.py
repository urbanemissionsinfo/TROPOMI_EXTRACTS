import os
import glob
import geopandas as gpd 
import rasterio
import numpy as np
import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 2:
    print("Usage: python scripts/regrid.py pollutant")
    sys.exit(1)

pollutant = sys.argv[1].upper()

path = os.getcwd() + '/data/AllIndia_{}_tifs/'.format(pollutant)
grids = gpd.read_file('assets/india_grid/grids-0.1x0.1deg/grids_india.shp')

tifs = glob.glob(path+'/*.tif')

for tif in tqdm(tifs):
    filename = 'regridded_' + tif.split('/')[-1].split('.')[0] 
    regrid_folder_path = os.getcwd() + '/data/AllIndia_{}_regridded/'.format(pollutant)
    os.system("gdalwarp -t_srs EPSG:4326 -te 67 7 99 39 -tr 0.1 0.1 {} {} -co COMPRESS=DEFLATE -co TILED=YES".format(tif,
                                                                                                                     regrid_folder_path+filename+'.tif'))
    
    with rasterio.open(regrid_folder_path+filename+'.tif', 'r+') as raster:
        raster_array = raster.read(1)
    raster_array = np.flipud(raster_array)
    values = raster_array.flatten()

    grids['value'] = values 

    grids.to_file(regrid_folder_path + filename + '.geojson')
    grids.to_csv(regrid_folder_path + filename + '.csv')