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
if(QgsProject.instance().mapLayersByName('PointsWithLUNr lowSpeedLanduseID')==[]):
    processing.run("qgis:rastersampling",
    {'COLUMN_PREFIX' : 'LanduseNr',
    'INPUT' : 'C:\\Users\\janni\\OneDrive\\Dokumente\\UNI\\PythonInGIS\\project\\lowSpeed.shp',
    'OUTPUT' : shapefn,
    'RASTERCOPY' : 'C:/Users/janni/OneDrive/Dokumente/UNI/PythonInGIS/project/data/landuse/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7/product/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7.tif'})
    # This should be the same directory as you
    updated_shapefile = iface.addVectorLayer(shapefn, 'PointsWithLUNr', 'ogr')
else:
    updated_shapefile = QgsProject.instance().mapLayersByName('PointsWithLUNr lowSpeedLanduseID')[0]

# Plot the land uses of the resting points
def descriptiveStatisticsLandUse(layer):
    features = layer.getFeatures()
    # Create empty list for landuses
    list_lu = []
    # Iterate over features and add to a list
    for feature in features:
        list_lu.append(feature['LanduseNr_'])
    # bins of the landuse numbers
    bins = [10,11,30, 60, 70,90, 100,110,120,122,130,140,150,152,160,180,210]
    # Create histogram
    # plt.hist(list_lu, bins =  17, facecolor = 'g', density =True )
    # plt.xlabel('Landuse number')
    # plt.ylabel('Frequency')
    # plt.title('Histogram of landuses')
    # plt.grid(True)
    # plt.show()
    # make the histogram
    hist, bin_edges = np.histogram(list_lu,bins)
    fig,ax = plt.subplots()
    # Plot the histogram heights against integers on the x axis
    ax.bar(range(len(hist)),hist,width=1)
    # Set the ticks to the middle of the bars
    ax.set_xticks([0.5+i for i,j in enumerate(hist)])
    # Set the xticklabels to a string that tells us what the bin edges were
    ax.set_xticklabels(['{} - {}'.format(bins[i],bins[i+1]) for i,j in enumerate(hist)])
    plt.show()

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

# Function to convert Id of landuse to name
# Still TODO!
def convertIdToName(mylegend, shapelayer):
    # Check for editing rights (capabilities)
    caps = shapelayer.dataProvider().capabilities()
    print(caps)
    print("Starting iterating over Features")
    features = shapelayer.getFeatures()
    # Get field ID of landuse nr
    luIDFieldID = shapelayer.fields().indexFromName("LanduseNr_")
    i = 0
    # Initiate a variable to hold the attribute values
    updates = {}
    # iterate over features
    for feat in features:
        # for row in mylegend:
        #     if(i<3):
        #         print("The legend entry {} of first column has datatype: {}".format(row[0],type(row[0])))
        #         print("Type of feature entry {} in column luIDFieldID: {}".format(feat[luIDFieldID],type(feat[luIDFieldID])))
        #         i= i+1
        #
        #     if(int(row[0])==int(feat[luIDFieldID])):
        #         luName = row[1]
        luNameFieldID = shapelayer.fields().indexFromName("Landuse")
        if i<5:
            print(feat[0])
            print("Field ID: {} and replacing VALUE: {}".format(luNameFieldID, int(feat[luIDFieldID])))
            print("Feature id: {}".format(id(feat)))
            i = i+1
        attrs = {luNameFieldID: int(feat[luIDFieldID])}
        # Update the field in the shapefile
        updates[feat.id()] = {luNameFieldID: int(feat[luIDFieldID])}
    print(updates)
    # Use the created dictionary to update the field for all features
    #shapelayer.dataProvider().changeAttributeValues(updates)
    # Update to propagate the changes
    #shapelayer.updateFields()

convertIdToName(legend,updated_shapefile)
#QgsProject.instance().removeMapLayer(rlayer.id())
print("DONE! :)")
