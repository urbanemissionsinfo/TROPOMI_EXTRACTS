import glob
import os
from collections import Counter

csvs = glob.glob(os.getcwd()+'/data/HCHO_csvs/*.csv')

cities = []
for csv in csvs:
    cities.append(csv.split('/')[-1].split('_')[0])


print(Counter(cities))