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

service_account = 'ueinfo@ueinfo.iam.gserviceaccount.com '
credentials = ee.ServiceAccountCredentials(service_account, 'ueinfo-3a6879e85ef2.json')

ee.Initialize(credentials)

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


def download_tifs(pollutant, airshed_shp):
    tic = time.perf_counter()

    year=2020
    airshed_box, aoi = get_aoi(airshed_shp)
    
    airshed_name = airshed_shp.split('/')[-1].split('.')[0][6:]
    print('----***-----*-----***----')
    print("Downloading TIFs for the airshed: ",airshed_name)
    print('----***-----*-----***----')

    if year ==2023:
        max_month=8
    else:
        max_month=13
    for month in range(1,max_month):
        print('----')
        print('Downloading for month: ', month)
        print('----')
    
        #Image Collection - l3_NO2 satellite -- SELECTING only two bands (NO2 Column Number density and Cloud_fraction)
        if pollutant=='SO2':
            band_name = 'SO2_column_number_density'
        elif pollutant == 'HCHO':
            band_name = 'tropospheric_HCHO_column_number_density'
        elif pollutant == 'NO2':
            band_name = 'NO2_column_number_density'
        else:
            band_name = 'O3_column_number_density'
            
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_'+pollutant).select([band_name, 'cloud_fraction'])
        if month <9:
            startDate = str(year)+'-0'+str(month)+'-01'
            endDate = str(year)+'-0'+str(month)+'-15'
        elif month==9:
            startDate = str(year)+'-0'+str(month)+'-01'
            endDate = str(year)+'-'+str(month)+'-15'
        elif month<12:
            startDate = str(year)+'-'+str(month)+'-01'
            endDate = str(year)+'-'+str(month)+'-15'
        else:
            startDate = str(year)+'-'+str(month)+'-01'
            endDate = str(year)+'-'+str(month)+'-15'

        if os.getcwd()+'/data/'+pollutant+'_csvs/'+airshed_name+'_15dayavg'+'_'+pollutant.lower()+'_'+startDate+'.csv' in glob.glob(os.getcwd()+'/data/'+pollutant+'_csvs/*.csv'):
           continue
        else:
           pass
        
        
        #Filter image collection -- filtered for date range, chennai_box range,
        fortnight=0
        while fortnight<2:
            filtered = collection.filter(ee.Filter.date(startDate, endDate)).filter(ee.Filter.bounds(aoi))
            #Apply the maskClouds and clip_image function to each image in the image collection.
            cloudMasked = filtered.map(maskClouds).select(band_name)
            clipped_images = cloudMasked.map(clip_image(aoi))
        
            #Export image
            #geemap.ee_export_image(image, filename='bishek/NO2_tifs/'+airshed_name+'_15dayavg_'+'no2_'+startDate+'.tif',
             #                  scale=30,              #                 region=aoi, file_per_band=True)
        
            ## To download aggregated data for the given airshed box in the form of a csv.
            geemap.zonal_statistics(clipped_images.median(),
                                    airshed_box,
                                    os.getcwd()+'/data/'+pollutant+'_csvs/'+airshed_name+'_15dayavg'+'_'+pollutant.lower()+'_'+startDate+'.csv',
                                    statistics_type='MEAN',
                                    scale=30)
            
            # To download all tif images of a collection 
            geemap.ee_export_image(clipped_images.median(),
                       filename=os.getcwd()+'/data/'+pollutant+'_tifs/'+airshed_name+'_15dayavg'+'_'+pollutant.lower()+'_'+startDate+'.tif',
                       scale=1000,
                       region=aoi,
                       file_per_band=True)

            print(startDate+'xx'+endDate)
            startDate = startDate[:-2]+'16'
            if month==2:
                endDate = endDate[:-2]+'28'
            elif month in [4,6,9,11]:
                endDate = endDate[:-2]+'30'
            else:
                endDate = endDate[:-2]+'31'
        
            fortnight = fortnight+1


    toc = time.perf_counter()
    print('Time taken {} seconds'.format(toc-tic))


pool= ThreadPool(processes=3)
#pool.map(download_tifs,['SO2','HCHO','O3'])

airsheds = glob.glob(os.getcwd()+"/data/gridextents_shponly/*.shp")

args= []
for airshed in tqdm(airsheds):
    #print(airshed)
    args.append(['NO2', airshed])
    #download_tifs('NO2', airshed)

pool.starmap(download_tifs, args)