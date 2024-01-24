# TROPOMI_EXTRACTS
Scripts to gather Tropomi Extracts for airsheds

## How to run the script?

1. `tropomiextract.py` code helps in extracting TROPOMI dataset for a given airshed. It downloads a tif image and a csv for a 15 day average period. `HCHO`, `NO2`, `SO2`, `O3` pollutants are covered in this code. There are only two user inputs needed (inside code) to execute this script:
    a. `pollutant_to_extract` - one of these `HCHO`, `NO2`, `SO2`, `O3` 
    b. `year_to_extract` - 2019 onwards.

Example usage: `python scripts/tropomiextract.py NO2 2023`

2. Ideally, you would have 24 csvs per year. But due to connectivity issues, the above code would skip producing a few csvs. Use `check.py` to see which airsheds have incomplete extracts.

3. `dataprocess.py`: Once all csvs are downloaded, Run this code to create a single timeseries csv for each airshed. These csvs are stored in timeseries csv.

Example usage: `python scripts/dataprocess.py NO2`

4. `plot.py`: If you want to see the timeseries plot based on the timeseries CSVs produced above.
Example usage: `python scripts/plot.py NO2 hyderabad`

