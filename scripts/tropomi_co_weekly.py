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
if len(sys.argv) < 3:
    print("Usage: python scripts/tropomi_co_weekly.py pollutant_to_extract year_to_extract")
    sys.exit(1)

service_account = 'ueinfo@ueinfo.iam.gserviceaccount.com '
credentials = ee.ServiceAccountCredentials(service_account, 'ueinfo-615e315d9158.json')

ee.Initialize(credentials)

# USER INPUTS
pollutant_to_extract = sys.argv[1]
year_to_extract = int(sys.argv[2])

def get_aoi(airshed_shp):
    airshed_box = geemap.shp_to_ee(airshed_shp)
    aoi = airshed_box.geometry()
    return airshed_box, aoi

def clip_image(roi):
    def call_image(image):
        return image.clip(roi)
    return call_image


def download_tifs(pollutant, airshed_shp):
    tic = time.perf_counter()

    year=year_to_extract ## YEAR FOR WHICH DATA NEEDS TO BE DOWNLOADED - USER INPUT
    airshed_box, aoi = get_aoi(airshed_shp)
    
    airshed_name = 'PUNJAB'
    print('----***-----*-----***----')
    print("Downloading TIFs for the airshed: ",airshed_name)
    print('----***-----*-----***----')

   
    
    min_month = 1 # USER INPUT - MONTH START
    max_month = 12

    date_from = str(year)+'-'+str(min_month)+'-01'
    date_to = str(year)+'-'+str(max_month)+'-11'

    date_start = datetime.strptime(date_from, "%Y-%m-%d").replace(day=1)

    print('----')
    print('Downloading for year: ', year)
    print('----')

    while date_start < datetime.strptime(date_to, "%Y-%m-%d"):
        # Calculate the first day of the next month (date_end)
        date_end = date_start + timedelta(days=6)
        next_week = date_start + timedelta(days=7)
        # Convert the first day of the next month to a formatted date string
        date_end = date_end.strftime("%Y-%m-%d")
        next_week = next_week.strftime("%Y-%m-%d")
        date_start = date_start.strftime("%Y-%m-%d")

        print(date_end)
        print(date_start)



        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_'+pollutant).select(['CO_column_number_density'])
        #Filter image collection -- filtered for date range, airshed range
        filtered = collection.filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.bounds(aoi))
        #Apply the maskClouds and clip_image function to each image in the image collection.
        clipped_images = filtered.map(clip_image(aoi))
        
        ## To download aggregated data for the given airshed box in the form of a csv.
        folder_path = os.getcwd()+'/data/{}_{}_weekly_tifs/'.format(airshed_name, pollutant)
        if not os.path.exists(folder_path[:-1]):
            os.makedirs(folder_path[:-1])
        geemap.zonal_statistics(clipped_images.median(),
                            airshed_box,
                            folder_path+airshed_name+'_weeklyavg'+'_'+pollutant.lower()+'_'+date_start+'.csv',
                            statistics_type='MEAN',
                            scale=11000)
        
        # To download all tif images of a collection
        geemap.ee_export_image(clipped_images.median(),
                            filename=folder_path+airshed_name+'_weeklyavg'+'_'+pollutant.lower()+'_'+date_start+'.tif',
                            scale=11000,
                            region=aoi,
                            file_per_band=True)
        
        date_start = datetime.strptime(next_week, "%Y-%m-%d")
        
    toc = time.perf_counter()
    print('Time taken {} seconds'.format(toc-tic))


pool= ThreadPool(processes=1)
#pool.map(download_tifs,['SO2','HCHO','O3'])

airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/Punjab_shp/Punjab.shp"
#airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/centralasia_adm0/centralasia_adm0_select.shp"

args= []
args.append([pollutant_to_extract, airshed])

pool.starmap(download_tifs, args)


