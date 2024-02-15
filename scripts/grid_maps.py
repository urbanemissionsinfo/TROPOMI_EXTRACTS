import os
import geopandas as gpd
import matplotlib.pyplot as plt
from mapclassify import FisherJenks, EqualInterval, NaturalBreaks, Quantiles, MaxP
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import glob
import re
import datetime
from tqdm import tqdm
from joblib import Parallel, delayed

def str_month_to_abbreviation(month_str):
    # Convert the string month to an integer
    month_int = int(month_str)

    # Convert the integer month to a datetime object
    date_obj = datetime.datetime.strptime(str(month_int), "%m")

    # Format the datetime object to get the three-letter month abbreviation
    month_abbreviation = date_obj.strftime("%b")

    return month_abbreviation

regridded_geojsons = glob.glob(os.getcwd() + "/data/AllIndia_NO2_regridded/*.geojson")

colors = ['#ffffff', #white
          '#289e4b', #green
          '#9ad9ad', #lighgreen
          '#f5fc17', #yellow
          '#e88a27', #orange
          '#f50717' #red
          ]  # Define your colors
cmap_name = 'custom_cmap'

# Create the colormap
custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=6)


def bin(x):
    if x< 0.00005:
        return 0 #white
    elif x < 0.00006:
        return 1 #green
    elif x < 0.00008:
        return 2 #lightgreen
    elif x < 0.0001:
        return 3 #yellow
    elif x < 0.00012:
        return 4 #orange
    else:
        return 5 #red


# Load base map shapefile
base_map = gpd.read_file(os.getcwd() + "/assets/INDIA_STATES.geojson")

def download_tropomi_india(geojson):
    year = re.findall(r'\d{4}', geojson)[0]
    month = re.findall(r'\d{2}', geojson)[2]
    month_str = str_month_to_abbreviation(month).upper()
    print(year + '-' + month_str)

    # Load grid data shapefile
    grid_data = gpd.read_file(geojson)
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 10))


    # Plot grid data on top of base map
    grid_data['bin'] = grid_data["value"].apply(bin)

    grid_data.plot(column='bin',
                cmap=custom_cmap,
                alpha=1,
                #legend=True,
                ax=ax)

    # Plot base map
    base_map.boundary.plot(ax=ax, color="black")

    # Add legend
    #plt.colorbar(label="Grid Values")

    # Set limits to tightly fit the data
    ax.set_xlim(grid_data.X1.min(), grid_data.X2.max())
    ax.set_ylim(grid_data.Y1.min(), grid_data.Y2.max())


    # Add title
    plt.title("TROPOMI Retrievals Monthly Average for NO2 Columnar Density - {} {}".format(year, month_str))

    # Load the image
    logo = plt.imread(os.getcwd() + '/assets/UEinfo_logo3_resized.jpg')  # Provide the path to your image file
    plt.figimage(logo, xo=870, yo=40)

    legend_img = plt.imread(os.getcwd() + '/assets/gridchoropleth_legend_resized.png')  # Provide the path to your image file
    plt.figimage(legend_img, xo=735, yo=845)

    plt.tight_layout()
    # Show plot
    plt.savefig(os.getcwd() +"/plots/INDIABOX_TROPOMI_NO2_{}_{}.png".format(year, month),
                #dpi=50
                )


Parallel(n_jobs=4)(delayed(download_tropomi_india)(geojson) for geojson in regridded_geojsons)