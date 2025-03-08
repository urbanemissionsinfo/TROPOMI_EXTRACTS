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
import geopandas as gpd
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/tropomi_extract_annual.py airshed pollutant_to_extract year_to_extract")
    sys.exit(1)


service_account = 'ueinfo@ueinfo.iam.gserviceaccount.com '
credentials = ee.ServiceAccountCredentials(service_account, 'ueinfo-615e315d9158.json')

ee.Initialize(credentials)

# USER INPUTS
airshed_name = sys.argv[1] #CAPS
pollutant_to_extract = sys.argv[2]
year_to_extract = int(sys.argv[3])

def get_aoi(airshed_shp):
    airshed_box = geemap.shp_to_ee(airshed_shp)
    aoi = airshed_box.geometry()
    return airshed_box, aoi

def maskClouds(image):
    mask = image.select('cloud_fraction').lt(0.1)
    return image.updateMask(mask)

# clip_image function clips the satellite image to our given area of interest
# https://gis.stackexchange.com/questions/302760/gee-imagecollection-map-with-multiple-input-function
def clip_image(roi):
    def call_image(image):
        return image.clip(roi)
    return call_image

def bitwiseExtract(input, fromBit, toBit):
    maskSize = ee.Number(1).add(toBit).subtract(fromBit)
    mask = ee.Number(1).leftShift(maskSize).subtract(1)
    return input.rightShift(fromBit).bitwiseAnd(mask)

def aod_mask(image):
    aod_qa_band = image.select('AOD_QA')
    cloudMask = bitwiseExtract(aod_qa_band, 0, 2).eq(1)
    aodqaMask = bitwiseExtract(aod_qa_band, 8, 11).eq(0)
    mask = cloudMask.And(aodqaMask)
    return image.updateMask(mask)

def download_tifs(pollutant, airshed_shp):
    tic = time.perf_counter()

    year=year_to_extract ## YEAR FOR WHICH DATA NEEDS TO BE DOWNLOADED - USER INPUT
    airshed_box, aoi = get_aoi(airshed_shp)
    
    print('----***-----*-----***----')
    print("Downloading TIFs for the airshed: ",airshed_name.upper())
    print('----***-----*-----***----')

    if year ==2024:
        max_month=1
    else:
        max_month=12
    
    min_month = 1 # USER INPUT - MONTH START

    date_from = str(year)+'-0'+str(min_month)+'-01'
    date_to = str(year+1)+'-0'+str(min_month)+'-01'
    date_start = datetime.strptime(date_from, "%Y-%m-%d").replace(day=1)
    # Calculate the first day of the next month (date_end)
    next_month = date_start + timedelta(days=367)
    date_end = next_month.replace(day=1)
    # Convert the first day of the next month to a formatted date string
    date_end = date_end.strftime("%Y-%m-%d")
    date_start = date_start.strftime("%Y-%m-%d")

    print(date_end)
    print(date_start)


    print('----')
    print('Downloading for year: ', year)
    print('----')
    
    #Image Collection - l3_NO2 satellite -- SELECTING only two bands (NO2 Column Number density and Cloud_fraction)
    if pollutant=='SO2':
        band_name = 'SO2_column_number_density'
    elif pollutant == 'HCHO':
        band_name = 'tropospheric_HCHO_column_number_density'
    elif pollutant == 'NO2':
        band_name = 'tropospheric_NO2_column_number_density'
    elif pollutant == 'CO':
        band_name = 'CO_column_number_density'
    else:
        band_name = 'O3_column_number_density'
        
    if pollutant == 'UVAI':
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI').select(['absorbing_aerosol_index'])
        #Filter image collection -- filtered for date range, airshed range
        filtered = collection.filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.bounds(aoi))
        clipped_images = filtered.map(clip_image(aoi))
    elif pollutant == "AOD":
        collection = ee.ImageCollection('MODIS/061/MCD19A2_GRANULES').select(['Optical_Depth_055', 'AOD_QA'])
        #Filter image collection -- filtered for date range, airshed range
        filtered = collection.filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.bounds(aoi))
        cloudMasked = filtered.map(aod_mask).select('Optical_Depth_055')
        clipped_images = cloudMasked.map(clip_image(aoi))
    else:
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_'+pollutant).select([band_name, 'cloud_fraction'])
        #Filter image collection -- filtered for date range, airshed range
        filtered = collection.filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.bounds(aoi))
        #Apply the maskClouds and clip_image function to each image in the image collection.
        cloudMasked = filtered.map(maskClouds).select(band_name)
        clipped_images = cloudMasked.map(clip_image(aoi))

    #collection = ee.ImageCollection('MODIS/061/MCD19A2_GRANULES').select(['Optical_Depth_055'])
    
    ## To download aggregated data for the given airshed box in the form of a csv.
    folder_path = os.getcwd()+'/data/{}_{}_yearly_tifs/'.format(airshed_name, pollutant)
    if not os.path.exists(folder_path[:-1]):
        os.makedirs(folder_path[:-1])
    # geemap.zonal_statistics(clipped_images.median(),
    #                        airshed_box,
    #                        folder_path+airshed_name+'_5yearlyavg'+'_'+pollutant.lower()+'_'+date_start+'.csv',
    #                        statistics_type='MEAN',
    #                        scale=12000)
    
    # To download all tif images of a collection
    geemap.ee_export_image(clipped_images.median(),
                           filename=folder_path+airshed_name+'_yearlyavg'+'_'+pollutant.lower()+'_'+date_start+'.tif',
                           scale=1000,
                           region=aoi,
                           file_per_band=True)
    
    toc = time.perf_counter()
    print('Time taken {} seconds'.format(toc-tic))


pool= ThreadPool(processes=1)
#pool.map(download_tifs,['SO2','HCHO','O3'])

airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/grids_{}/grids_{}.shp".format(airshed_name.lower(),
                                                                                        airshed_name.lower())
#airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/india_grid/india_grid.shp"
#airshed = r"C:/Users/dskcy/UEInfo/Rasterize_Grids/assets/indiagrids-0.1x0.1deg/grids_india.shp"

args= []
args.append([pollutant_to_extract, airshed])

pool.starmap(download_tifs, args)