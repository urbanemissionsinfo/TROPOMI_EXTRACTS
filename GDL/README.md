# GDL

## How to manually download from Copernicus Data Space
[Video](https://www.youtube.com/watch?v=f39LMyPyoqI)

## How to get creds on Copernicus Data Space
1. Open Copernicus DataSpace: [Link](https://dataspace.copernicus.eu/copernicus-data-space-ecosystem-dashboard)
2. Register/Login
3. Click on `My Account`. Your Account Console will open.
4. Under Dashboards, Click on `Sentinel Hub`
5. Click on `User Settings`
6. Create a new OAuth Client - store client_secret and client_id.

## How to run scripts?

1. To download the data using API: Use the Python script. In this Python script you’ll need to modify the download directory (Line 60) and the query timeframe (Line 65). For Line 65, the exact dates are in this format “yyyyMMdd”; I’ve included the timeframe as the default. In Line 68, you can toggle between ‘Near real time’ and ‘Offline’; I am assuming you want Offline, so I’ve included that as the default. The GeoJSON file is currently set to your domain covering India. If you need to substitute the lat/lons, open the file and modify to the corner points of your domain in this file (repeating the first corner point twice to “close” the box). That should be self-explanatory. And then make sure that file is located in the same directory as the Python script (when you run the Python script).

2. To re-grid the data: Use regrid_tropomi_no2.pro. All variables to toggle are within the first 35 lines of the code. Make sure to modify the directory to your system.

3. To average the data: Use write_tropomi_no2.pro. Again all variables to toggle are within the first 30ish lines of the code. Again make sure to modify the directory to your system.