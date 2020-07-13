# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import csv
from collections import Counter
import gdal
# import rasterio as rio
# from rasterio.plot import plotting_extent
# import earthpy as et
# import earthpy.plot as ep

def preProcessLegend(filename):
    """
    Preprocess legend
        Parameter:
            filename(String): Path to landuse legend
        Returns:
            Preprocessed legend
    """
    # empty list for the landuse legend
    results = []
    # read csv file
    with open(filename, newline = '', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile,delimiter=';')
        for row in reader: # each row is a list
            results.append(row)
    return results

def rasterToList(ds, legend):
    """
    Convert raster values to list
        Parameter:
            ds (QgsMapLayer): Raster object
            filename(String): Path to landuse legend
        Returns:
            Raster values as a list
    """
    data_arr = ds.ReadAsArray()
    # remove mulit dimensionality
    data_flattened = data_arr.flatten()
    # convert to list
    data_list = data_flattened.tolist()
    results=[]
    # Convert number to labels of landuses
    for i in data_list:
        for row in legend:
            if(i == int(row[0])):
                results.append(row[1])
                break
    return results

def plotList(list):
    """
    Plot list
        Parameter:
            list(list): List
    """
    counts = Counter(list)
    keys = counts.keys()
    values = counts.values()
    fig, ax = plt.subplots()
    data = [float(v) for v in values]
    wedges, texts, autotexts= ax.pie(data, labels=None,autopct='%1.2f')
    ax.legend(wedges, keys, title = "Landuse types", loc="right",bbox_to_anchor=(1.6,0.5))
    ax.set_title("Landuses overall")
    plt.show()


def main():
    """
    Main function calling the other functions.
    """
    # Path to data dir
    data_dir = os.path.join("C:\\","Users","janni","OneDrive","Desktop","data")

    # Path to clipped raster file
    rast_fn = os.path.join(data_dir, 'clipped_Eurasia_Landcover.tif')

    # Path to raster legend
    landuse_legend_fn = os.path.join(data_dir,'Eurasia_Landcover_Legend.csv')

    # Preprocess legend
    rast_legend = preProcessLegend(landuse_legend_fn)

    # Open raster file
    rast = gdal.Open(rast_fn)

    # load numpy array
    data = rasterToList(rast,rast_legend)

    # Plot as pie
    plotList(data)

main()
print("DONE")
