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
import sys

# Check if there are enough command line arguments
if len(sys.argv) < 4:
    print("Usage: python scripts/grid_maps.py extent pollutant freq")
    sys.exit(1)

extent = sys.argv[1].upper()
pollutant = sys.argv[2].upper()
freq = sys.argv[3].lower()

if freq not in ['yearly','monthly']:
    print("Usage: freq should be monthly or yearly")
    sys.exit(1)

# Load base map shapefile
#base_map = gpd.read_file(os.getcwd() + "/assets/east_africa_adm0/east_africa_adm0.shp")
#base_map = gpd.read_file(os.getcwd() + "/assets/India_states2023/Admin2.shp")
#base_map = gpd.read_file(os.getcwd() + "/assets/philippines_adm0/philippines_adm0.shp")
base_map = gpd.read_file(os.getcwd() + "/assets/mainlandseasia_adm0/mainlandseasia_adm0.shp")

regridded_geojsons = glob.glob(os.getcwd() + "/data/{}_{}_regridded_{}/*.geojson".format(extent, pollutant, freq))

# TO MASK
base_map['common'] = 'c'
boundary = base_map.dissolve('common')
boundary = boundary.set_crs('EPSG:4326')
boundary.drop(['Maille'],axis=1,inplace=True)
#grids = gpd.read_file("assets/grids_philippines/00.grids/grids_philippines.shp")
grids = gpd.read_file(os.getcwd() + "/assets/mainlandseasia/00a_grids/grids_mainlandseasia.shp")

grids = grids.set_crs('EPSG:4326')
#grids_df_masked = gpd.sjoin(grids, boundary, predicate='intersects') 
grids_df_masked = grids
def str_month_to_abbreviation(month_str):
    # Convert the string month to an integer
    month_int = int(month_str)

    # Convert the integer month to a datetime object
    date_obj = datetime.datetime.strptime(str(month_int), "%m")

    # Format the datetime object to get the three-letter month abbreviation
    month_abbreviation = date_obj.strftime("%b")

    return month_abbreviation


colors_gases = ['#ffffffff', # white
          '#289e4bff', # dark green
          '#9ad9adff', #light green
          '#00ffffff', #cyan
          '#f5fc17ff', #yellow
          '#e88a27ff', #orange
          '#f50717ff' #red
          ]  # Define your colors

colors_UVAI = ['#073763ff', 
          '#0057ffff',
          '#00ffffff',
          '#b7b7b7ff', 
          '#595959ff', 
          '#ff9900ff', 
          '#832401ff' 
          ]  # Define your colors
cmap_name = 'custom_cmap'
# Create the colormap

if pollutant in ["UVAI", "AOD"]:
    custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors_UVAI, N=len(colors_UVAI))
else:
    custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors_gases, N=len(colors_gases))


def bin(x):
    if x< 0.99/10:
        return 0 
    if x < 1.06/10:
        return 1 
    elif x < 1.12/10 :
        return 2
    elif x < 1.19/10:
        return 3 
    elif x < 1.25/10:
        return 4 
    elif x < 1.32/10:
        return 5 
    else:
        return 6 


def plot_tropomi_india(geojson):
    year = re.findall(r'\d{4}', geojson)[0]
    month = re.findall(r'\d{2}', geojson)[2]
    month_str = str_month_to_abbreviation(month).upper()
    print(year + '-' + month_str)

    # Load grid data shapefile
    grid_data = gpd.read_file(geojson)
    grid_data = grid_data[grid_data['Maille'].isin(grids_df_masked.Maille.to_list())]

    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 10)) #10,10


    # Plot grid data on top of base map
    grid_data['bin'] = grid_data["value"].apply(bin)
    grid_data[['X1', 'X2', 'Y1', 'Y2']] = grid_data[['X1', 'X2', 'Y1', 'Y2']].astype(float)

    
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

    plt.xticks(fontweight='bold', fontsize=12)
    plt.yticks(fontweight='bold', fontsize=12)


    # Add year - month annotation
    bbox_props = dict(boxstyle="square,pad=0.3", fc="white", ec="black", lw=1)

    if freq=="yearly":
        file_name = "/{}_{}_{}.png".format(extent, pollutant, year)
        annotation = '{}'.format(year)
    else:
        file_name = "/{}_{}_{}_{}.png".format(extent, pollutant, year, month)
        annotation = '{}-{}'.format(month_str, year)

    plt.text(108.8, 8.3, #Choose Lat Long coords
             annotation,
             fontsize=16, fontweight='bold', color='black',
             ha='center', va='center',
             bbox=bbox_props)


    # Add title
    if pollutant == "UVAI":
        plt.title("UVAI Index", fontsize=20, fontweight='bold')
    elif pollutant =="AOD":
        plt.title("MODIS AOD", fontsize=20, fontweight='bold')
    else:
        plt.title("TROPOMI Retrievals - {}".format(pollutant), fontsize=20, fontweight='bold')

    # # Load the image
    #logo = plt.imread(os.getcwd() + '/assets/UEinfo_logo3_resized_25.jpg')  # Provide the path to your image file
    #plt.figimage(logo, xo=65, yo=20)
    
    legend_img = plt.imread(os.getcwd() + '/assets/{}_{}_legend_100.png'.format(extent.lower(), pollutant.lower()))  # Provide the path to your image file
    plt.figimage(legend_img, xo=66, yo=20)
    
    #plt.tight_layout()
    # # Show plot
    plots_folder = os.getcwd() +"/plots/{}_{}_{}".format(extent, pollutant, freq)
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)

    fig.tight_layout()

    plt.savefig(plots_folder + file_name,
                dpi=50
                )


Parallel(n_jobs=4)(delayed(plot_tropomi_india)(geojson) for geojson in regridded_geojsons)

#plot_tropomi_india(regridded_geojsons[6])