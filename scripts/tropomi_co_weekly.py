import ee
import geemap
import os
from datetime import datetime, timedelta
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 3:
    print("Usage: python scripts/tropomi_co_weekly.py pollutant_to_extract year_to_extract")
    sys.exit(1)

# Initialize Earth Engine
service_account = 'ueinfo@ueinfo.iam.gserviceaccount.com '
credentials = ee.ServiceAccountCredentials(service_account, 'ueinfo-615e315d9158.json')
ee.Initialize(credentials)

# Get command line arguments
pollutant_to_extract = sys.argv[1]
year_to_extract = int(sys.argv[2])

def get_aoi(airshed_shp):
    airshed_box = geemap.shp_to_ee(airshed_shp)
    return airshed_box, airshed_box.geometry()

def clip_image(roi):
    def call_image(image):
        return image.clip(roi)
    return call_image


def download_tifs(pollutant, airshed_shp):
    # Setup
    airshed_box, aoi = get_aoi(airshed_shp)
    airshed_name = 'PUNJAB'
    print(f"Downloading TIFs for {airshed_name} - Year: {year_to_extract}")
    
    # Initialize dates
    date_start = datetime(year_to_extract, 1, 1)
    date_end = datetime(year_to_extract, 12, 11)
    
    # Create output directory
    folder_path = os.path.join(os.getcwd(), 'data', f'{airshed_name}_{pollutant}_weekly_tifs')
    os.makedirs(folder_path, exist_ok=True)

    while date_start < date_end:
        week_end = date_start + timedelta(days=6)
        next_week = date_start + timedelta(days=7)
        
        date_start_str = date_start.strftime("%Y-%m-%d")
        date_end_str = week_end.strftime("%Y-%m-%d")

        # Get and process imagery
        collection = ee.ImageCollection(f'COPERNICUS/S5P/OFFL/L3_{pollutant}') \
            .select(['CO_column_number_density']) \
            .filter(ee.Filter.date(date_start_str, date_end_str)) \
            .filter(ee.Filter.bounds(aoi)) \
            .map(clip_image(aoi))
        
        median_img = collection.median()
        
        # Export data
        base_filename = os.path.join(folder_path, f'{airshed_name}_weeklyavg_{pollutant.lower()}_{date_start_str}')
        
        geemap.zonal_statistics(median_img, airshed_box, 
                              f'{base_filename}.csv',
                              statistics_type='MEAN', scale=11000)
        
        geemap.ee_export_image(median_img, filename=f'{base_filename}.tif',
                              scale=11000, region=aoi, file_per_band=True)
        
        date_start = next_week

# Run download for single pollutant
airshed = r"C:/Users/dskcy/UEInfo/TROPOMI_EXTRACTS/assets/Punjab_shp/Punjab.shp"
download_tifs(pollutant_to_extract, airshed)
