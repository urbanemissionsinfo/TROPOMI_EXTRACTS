import requests
import os
import sys
from datetime import datetime, date
from os.path import expanduser, exists
import urllib.request as ur
import pandas as pd
import shutil
import numpy as np
from pathlib import Path
from tqdm import tqdm
from functools import partial
from multiprocessing.pool import ThreadPool, Pool
from os import cpu_count, makedirs
import sys
from sentinelsat.sentinel import (
    SentinelAPI,
    geojson_to_wkt,
    read_geojson,
    InvalidChecksumError,
    SentinelAPIError,
)

today = date.today()

def fetch_product(file_id, api, products, download_dir):

    if not exists(download_dir / f"{products[file_id]['title']}.nc"):

        tqdm.write(f"File {file_id} not found. Downloading into {download_dir}")

        try:
            api.get_product_odata(file_id)
        except SentinelAPIError:
            tqdm.write(f"Error: File {file_id} not found in Hub. Skipping")
        else:
            while True:
                try:
                    api.download(
                        file_id,
                        directory_path=download_dir,
                        checksum=True,
                    )
                except InvalidChecksumError:
                    tqdm.write(
                        (f"Invalid checksum error in {file_id}. "
                        "Trying again...")
                    )
                    continue
                else:
                    tqdm.write(f"File {file_id} successfully downloaded")
                    break
    else:
        tqdm.write(f"File {file_id} already exists")

DHUS_USER = "s5pguest"
DHUS_PASSWORD = "s5pguest"
DHUS_URL = "https://s5phub.copernicus.eu/dhus"

DOWNLOAD_DIR = Path("E:\Goldberg\TROPOMI/NRT")

api = SentinelAPI(DHUS_USER, DHUS_PASSWORD, DHUS_URL)

query_body = {
        "date": ("20220101", "20220331"),
        "platformname": "Sentinel-5 Precursor",
        "producttype": 'L2__NO2___',
        "processingmode": 'Offline'
    }
footprint = geojson_to_wkt(read_geojson("map.geojson"))
products = api.query(footprint, **query_body)

# display results
tqdm.write(
    (
        "Number of products found: {number_product}\n"
        "Total products size: {size:.2f} GB\n"
    ).format(
        number_product=len(products),
        size=api.get_products_size(products)
        )
)

# list of uuids for each product in the query
ids_request = list(products.keys())

if len(ids_request) == 0:
    tqdm.write("Done!")
    sys.exit(0)

# list of downloaded filenames urls
filenames = [
    DOWNLOAD_DIR / f"{products[file_id]['title']}.nc"
    for file_id in ids_request
]

makedirs(DOWNLOAD_DIR, exist_ok=True)

with ThreadPool(2) as pool:
    pool.map(
        partial(
            fetch_product,
            api=api,
            products=products,
            download_dir=DOWNLOAD_DIR
        ),
        ids_request)

    pool.close()
    pool.join()

