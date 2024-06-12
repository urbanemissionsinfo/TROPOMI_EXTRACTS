import ee
import geemap
import pandas as pd
import numpy as np
import time
import glob
import os
from joblib import Parallel, delayed
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from tqdm import tqdm
from datetime import datetime, timedelta

import sys

# Check if there are enough command line arguments
if len(sys.argv) < 2:
    print("Usage: python scripts/uvai.py year_to_extract")
    sys.exit(1)


service_account = 'ueinfo@ueinfo.iam.gserviceaccount.com '
credentials = ee.ServiceAccountCredentials(service_account, 'ueinfo-615e315d9158.json')

ee.Initialize(credentials)

# USER INPUTS
year_to_extract = int(sys.argv[1])

def get_aoi(airshed_shp):
    airshed_box = geemap.shp_to_ee(airshed_shp)
    aoi = airshed_box.geometry()
    return airshed_box, aoi

# clip_image function clips the satellite image to our given area of interest
# https://gis.stackexchange.com/questions/302760/gee-imagecollection-map-with-multiple-input-function
def clip_image(roi):
    def call_image(image):
        return image.clip(roi)
    return call_image


def download_tifs(airshed_shp):
    tic = time.perf_counter()

    year=year_to_extract ## YEAR FOR WHICH DATA NEEDS TO BE DOWNLOADED - USER INPUT
    airshed_box, aoi = get_aoi(airshed_shp)
    
    airshed_name = 'PHILIPPINES'
    print('----***-----*-----***----')
    print("Downloading TIFs for the airshed: ",airshed_name)
    print('----***-----*-----***----')

    if year ==2024:
        max_month=1
    else:
        max_month=12
    
    min_month = 1 # USER INPUT - MONTH START

    date_from = str(year)+'-0'+str(min_month)+'-01'
    date_to = str(year+1)+'-0'+str(min_month)+'-01'
    date_start = datetime.strptime(date_from, "%Y-%m-%d").replace(day=1)
    while date_start < datetime.strptime(date_to, "%Y-%m-%d"):
        # Calculate the first day of the next month (date_end)
        next_month = date_start + timedelta(days=32)
        date_end = next_month.replace(day=1)
        # Convert the first day of the next month to a formatted date string
        date_end = date_end.strftime("%Y-%m-%d")
        date_start = date_start.strftime("%Y-%m-%d")

        #  # To skip already downloaded csv
        # if os.getcwd()+'/data/AllIndia_'+pollutant+'_csvs/'+airshed_name+'_monthlyavg'+'_'+pollutant.lower()+'_'+date_start+'.csv' in glob.glob(os.getcwd()+'/data/AllIndia_'+pollutant+'_csvs/*.csv'):
        #     date_start = datetime.strptime(date_end, "%Y-%m-%d").replace(day=1)  
        #     continue


        print('----')
        print('Downloading for month: ', date_start)
        print('----')
    
        
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI').select(['absorbing_aerosol_index'])
        

        #Filter image collection -- filtered for date range, airshed range
        filtered = collection.filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.bounds(aoi))
        #Apply the maskClouds and clip_image function to each image in the image collection.
        clipped_images = filtered.map(clip_image(aoi))
        
        
    
        ## To download aggregated data for the given airshed box in the form of a csv.
        folder_path = os.getcwd()+'/data/'+airshed_name+'_UVAI_csvs'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        geemap.zonal_statistics(clipped_images.median(),
                                airshed_box,
                                folder_path+'/'+airshed_name+'_monthlyavg'+'_uvai'+'_'+date_start+'.csv',
                                statistics_type='MEAN',
                                scale=11000)
        
        # To download all tif images of a collection 
        folder_path = os.getcwd()+'/data/'+airshed_name+'_UVAI_tifs'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        geemap.ee_export_image(clipped_images.median(),
                    filename=folder_path+'/'+airshed_name+'_monthlyavg'+'_uvai'+'_'+date_start+'.tif',
                    scale=11000,
                    region=aoi,
                    file_per_band=True)
        
        date_start = datetime.strptime(date_end, "%Y-%m-%d").replace(day=1)        

    toc = time.perf_counter()
    print('Time taken {} seconds'.format(toc-tic))


pool= ThreadPool(processes=1)

#airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/gridextents_ea/grids_eastafrica.shp"
#airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/india_grid/india_grid.shp"
airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/grids_philippines/00.gridextents/grids_philippines.shp"

args= []
args.append([airshed])

pool.starmap(download_tifs, args)