import os, ogr, osr, datetime, math, gdal, time, csv
from qgis.core import *
from qgis.gui import *
import qgis.utils
import numpy as np
from matplotlib import pyplot as plt
import statistics
import processing

# load the point shapefile manually!
# access the active layer
point_layer = iface.activeLayer()
if not point_layer:
    print("Shape file failed to load!")
else: print("Shape file loaded!")

fn = r'C:\Users\janni\OneDrive\Dokumente\UNI\PythonInGIS\project\data\landuse\ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7\product\ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif'

# rlayer = iface.addRasterLayer(fn, 'Landuse')

#Add new colums
def newColumn (layer,FieldName,DataType):
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.AddAttributes:
        res = point_layer.dataProvider().addAttributes([QgsField(FieldName,DataType)])
# Update to propagate the changes
    point_layer.updateFields()

# Check if field already exists
if  point_layer.fields().indexFromName("Landuse") == -1:
    #Create field for store Date
    newColumn (point_layer,"Landuse", QVariant.String)

# fn of the new shapefile including resting points and landuse identifier
shapefn = 'C:/Users/janni/OneDrive/Dokumente/UNI/PythonInGIS/project/lowSpeedLanduseID.shp'

# Compute the land use dataset for resting points, You have to specify filenames of your system!
# INPUT: fn of the resting points
# OUTPUT: fn of the new shapefile including resting points and landuse identifier
# RASTERCOPY: fn of the landuse raster
if(QgsProject.instance().mapLayersByName('Update lowSpeedLanduseID')==[]):
    processing.run("qgis:rastersampling",
    {'COLUMN_PREFIX' : 'LanduseNr',
    'INPUT' : 'C:\\Users\\janni\\OneDrive\\Dokumente\\UNI\\PythonInGIS\\project\\lowSpeed.shp',
    'OUTPUT' : shapefn,
    'RASTERCOPY' : 'C:/Users/janni/OneDrive/Dokumente/UNI/PythonInGIS/project/data/landuse/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7/product/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif'})
    # This should be the same directory as you
    updated_shapefile = iface.addVectorLayer(shapefn, 'Update', 'ogr')
else:
    updated_shapefile = QgsProject.instance().mapLayersByName('Update lowSpeedLanduseID')[0]

# @see: https://stackoverflow.com/questions/40553332/finding-frequency-distribution-of-a-list-of-numbers-in-python
def freq(lst):
    d = {}
    for i in lst:
        if d.get(i):
            d[i] += 1
        else:
            d[i] = 1
    return d

# Creating autocpt arguments
def func(pct, allvalues):
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d} g)".format(pct, absolute)

from collections import Counter
# Plot the land uses of the resting points
def descriptiveStatisticsLandUse(layer, x):
    features = layer.getFeatures()
    # Create empty list for landuses
    list_lu = []
    # Iterate over features and add to a list
    for feature in features:
        list_lu.append(feature['Landuse'])
    # bins of the landuse numbers
    bins = [10,11,30, 60, 70,90, 100,110,120,122,130,140,150,152,160,180,210]
    if(x=="Hist"):
        # Create histogram
        plt.hist(list_lu, density = True, color="orange")
        plt.xlabel('Landuse type')
        plt.xticks(rotation = "vertical", size = "x-small", stretch =  'condensed')
        plt.ylabel('Frequency')
        plt.title('Histogram of landuses - resting points (speed below median)')
        plt.grid(True)
        plt.tight_layout()
        plt.subplots_adjust(bottom = 0.45)
        plt.show()

    # @see: https://stackoverflow.com/questions/25950695/how-to-generate-pie-chart-using-dict-values-in-python-3-4
    # @see: https://pythontic.com/visualization/charts/piechart
    # Create Piechart autopct='%1.2f',lambda pct: func(pct, data)
    elif(x=="Pie"):
        counts = Counter(list_lu)
        keys = counts.keys()
        values = counts.values()
        print(counts)
        fig, ax = plt.subplots()
        data = [float(v) for v in values]
        wedges, texts, autotexts = ax.pie(data, labels=None,autopct='%1.2f')
        ax.legend(wedges, keys, title = "Landuse types", loc="left", bbox_to_anchor=(1, 0.8))
        #plt.setp(autotexts)
        ax.set_title("Landuses: A pie")
        fig.subplots_adjust(left=0.0125)
        plt.show()
    # make the histogram
    # hist, bin_edges = np.histogram(list_lu,bins)
    # fig,ax = plt.subplots()
    # # Plot the histogram heights against integers on the x axis
    # ax.bar(range(len(hist)),hist,width=1)
    # # Set the ticks to the middle of the bars
    # ax.set_xticks([0.5+i for i,j in enumerate(hist)])
    # # Set the xticklabels to a string that tells us what the bin edges were
    # ax.set_xticklabels(['{} - {}'.format(bins[i],bins[i+1]) for i,j in enumerate(hist)])
    # plt.show()

# specify path to legend of landuse
landuseLegend = os.path.join(os.getcwd(),'data','landuse','ESACCI-LC-Legend.csv')
# Preprocess legend
def preProcessLegend(filename):
    # empty list for the landuse legend
    results = []
    # read csv file
    with open(filename) as csvfile:
        reader = csv.reader(csvfile,delimiter=';')
        for row in reader: # each row is a list
            results.append(row)
    # deletes columns we don't need
    for row in results:
        del row[4]
        del row[3]
        del row[2]
    # delete first row which labels the columns
    results.pop(0)
    return results

#descriptiveStatisticsLandUse(updated_shapefile)
legend = preProcessLegend(landuseLegend)

# Function to convert Id of landuse to label
def convertIdToName(mylegend, shapelayer):
    # Check for editing rights (capabilities)
    caps = shapelayer.dataProvider().capabilities()
    print(caps)
    print("Starting iterating over Features")
    features = shapelayer.getFeatures()
    # Get field ID of landuse nr
    luINTFieldID = shapelayer.fields().indexFromName("LUNrInt")
    # Initiate a variable to hold the attribute values
    updates = {}
    # iterate over features
    for feat in features:
        luNameFieldID = shapelayer.fields().indexFromName("Landuse")
        intLU = feat[luINTFieldID]
        stringLU = "NOT FOUND"
        for row in mylegend:
            if(intLU==int(row[0])):
                stringLU = row[1]
                #print("YUHUU! FOUND: {}".format(row[1]))
                break
        updates[feat.id()] = {luNameFieldID: stringLU}
    #print(updates)
    # Use the created dictionary to update the field for all features
    shapelayer.dataProvider().changeAttributeValues(updates)
    # Update to propagate the changes
    shapelayer.updateFields()

# Function for converting the float number of the landuse type to int
def convertIdFloatToInt(shapelayer):
    # Check for editing rights (capabilities)
    caps = shapelayer.dataProvider().capabilities()
    print(caps)
    print("Starting iterating over Features")
    features = shapelayer.getFeatures()
    # Get field ID of landuse nr
    luIDFieldID = shapelayer.fields().indexFromName("LanduseNr_")
    # Initiate a variable to hold the attribute values as integers
    updates = {}
    # Create the field if not already done with datatype INT
    if (shapelayer.fields().indexFromName("LUNrInt")==-1):
        newColumn(shapelayer, "LUNrInt", QVariant.Int)
    # iterate over features
    for feat in features:
        luINTFieldID = shapelayer.fields().indexFromName("LUNrInt")
        # Update the field in the shapefile the integer of lu
        updates[feat.id()] = {luINTFieldID: int(feat[luIDFieldID])}
    # Use the created dictionary to update the field for all features
    shapelayer.dataProvider().changeAttributeValues(updates)
    # Update to propagate the changes
    shapelayer.updateFields()

#convertIdFloatToInt(updated_shapefile)
#convertIdToName(legend,updated_shapefile)
descriptiveStatisticsLandUse(point_layer,"Pie")
#QgsProject.instance().removeMapLayer(rlayer.id())
print("DONE! :)")
