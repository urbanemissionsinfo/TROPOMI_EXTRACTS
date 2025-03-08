import os
import glob
import geopandas as gpd 
import rasterio
import numpy as np
import sys
from tqdm import tqdm

# Check if there are enough command line arguments
if len(sys.argv) < 4:
    print("Usage: python scripts/regrid.py extent pollutant freq")
    sys.exit(1)

extent = sys.argv[1].upper()
pollutant = sys.argv[2].upper()
freq = sys.argv[3].lower()

path = os.getcwd() + '/data/{}_{}_{}_tifs/'.format(extent, pollutant, freq)

if extent == 'INDIA':
    grids = gpd.read_file(os.getcwd()  + r"/assets/india_grid/grids-0.1x0.1deg/grids_india.shp")
elif extent == 'EAST AFRICA':
    grids = gpd.read_file(os.getcwd() + '/assets/grids_ea/grids_eastafrica.shp')
elif extent == 'PHILIPPINES':
    grids = gpd.read_file(os.getcwd()  + r"/assets/grids_philippines/00.grids/grids_philippines.shp")
elif extent == 'SEASIA':
    grids = gpd.read_file(os.getcwd()  + r"/assets/mainlandseasia/00a_grids/grids_mainlandseasia.shp")
elif extent == 'BANDUNG':
    grids = gpd.read_file(os.getcwd()  + r"/assets/grids_bandung/grids_bandung.shp")
else:
    print("Check extent grids file")
    sys.exit(1)

grids[['X1','X2','Y1','Y2']] = grids[['X1','X2','Y1','Y2']].astype(float)

tifs = glob.glob(path+"/*.tif")
#print(tifs[4].split("\\")[-1].split('.')[0])
for tif in tqdm(tifs):
    filename = 'regridded_' + tif.split("\\")[-1].split('.')[0]
    regrid_folder_path = os.getcwd() + '/data/{}_{}_regridded_{}/'.format(extent, pollutant, freq)
    if not os.path.exists(regrid_folder_path[:-1]):
        os.makedirs(regrid_folder_path[:-1])
    lat_min = grids.X1.min()
    lat_max = grids.X2.max()
    lon_min = grids.Y1.min()
    lon_max = grids.Y2.max()

    os.system("gdalwarp -t_srs EPSG:4326 -te {} {} {} {} -tr 0.1 0.1 {} {} -co COMPRESS=DEFLATE -co TILED=YES".format(lat_min, lon_min,
                                                                                                                      lat_max, lon_max,
                                                                                                                    tif,
                                                                                                                     regrid_folder_path+filename+'.tif'))
    
    with rasterio.open(regrid_folder_path+filename+'.tif', 'r+') as raster:
        raster_array = raster.read(1)
    raster_array = np.flipud(raster_array)
    values = raster_array.flatten()

    grids['value'] = values 
    #grids.to_file(regrid_folder_path + filename + '.geojson')
    grids[['Maille', 'Maille_Y', 'Maille_X', 'value']].to_csv(regrid_folder_path + filename + '.csv')