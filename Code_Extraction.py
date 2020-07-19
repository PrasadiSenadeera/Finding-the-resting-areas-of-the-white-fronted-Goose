import os
import ogr
import csv
from qgis.core import *
from qgis.gui import *
import qgis.utils
import numpy as np
from matplotlib import pyplot as plt
import processing
from collections import Counter

def newColumn (layer,FieldName,DataType):
    """
    Adds a new field to the layer.
        Parameters:
            layer: QGIS layer object
            FieldName(String): Name of the new fields
            Datatype: QVariant DataType
    """
    # Check if field already exists
    if layer.fields().indexFromName(FieldName)==-1:
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddAttributes:
            res = layer.dataProvider().addAttributes([QgsField(FieldName,DataType)])
            print("New field \"{}\" added".format(FieldName))
        # Update to propagate the changes
        layer.updateFields()
    else:
        print("Field \"{}\" already exists.".format(FieldName))

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
    # deletes columns we don't need (spectral bands)
    """for row in results:
        del row[4]
        del row[3]
        del row[2]
    # delete first row which labels the columns
    results.pop(0)"""
    return results

def convertIdFloatToInt(shapelayer):
    """
    Function for converting the float number of the landuse type to int
        Parameters:
            shapelayer(QgsMapLayer): shapefile of resting points without landuse labels
    """

    # Check for editing rights (capabilities)
    caps = shapelayer.dataProvider().capabilities()
    print("Starting iterating over Features")
    features = shapelayer.getFeatures()
    # Get field ID of landuse nr
    luIDFieldID = shapelayer.fields().indexFromName("LanduseNr_")
    # Initiate a variable to hold the attribute values as integers
    updates = {}
    # Create the field if not already done with datatype INT
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

# Function to convert Id of landuse to label
def convertIdToName(mylegend, shapelayer):
    """
    Function to convert Id of landuse to label
        Parameters:
            mylegend(list): nested list including numbers and corresponding labels of Landuses
            shapelayer(QgsMapLayer): shapefile of resting points without landuse labels
    """
    # Check for editing rights (capabilities)
    caps = shapelayer.dataProvider().capabilities()

    #Create field for storing Landuse label (String)
    newColumn (shapelayer,"Landuse", QVariant.String)

    print("Starting iterating over Features")
    features = shapelayer.getFeatures()
    # Get field ID of landuse nr
    luINTFieldID = shapelayer.fields().indexFromName("LUNrInt")
    # Initiate a variable to hold the attribute values
    updates = {}
    i = 0
    # iterate over features
    for feat in features:
        luNameFieldID = shapelayer.fields().indexFromName("Landuse")
        intLU = feat[luINTFieldID]
        stringLU = "NOT FOUND"
        for row in mylegend:
            luID = row[0]
            #print("{} is a string! And will be converted to :{}".format(luID, int(luID)))
            if(intLU==int(luID)):
                stringLU = row[1]
                break
                #print("YUHUU! FOUND: {}".format(row[1]))
        updates[feat.id()] = {luNameFieldID: stringLU}
    # Use the created dictionary to update the field for all features
    shapelayer.dataProvider().changeAttributeValues(updates)
    # Update to propagate the changes
    shapelayer.updateFields()

def plotLandUse(layer, x):
    """
    Plot the land uses of the resting points
        Parameters:
            layer (QgsMapLayer): point layer of resting points and their corresponding landuse type
            x (String): Specifies type of plot (Hist or Pie)
    """
    # features of the layer
    features = layer.getFeatures()
    # Create empty list for landuses
    list_lu = []
    # Iterate over features and add to a list
    for feature in features:
        list_lu.append(feature['Landuse'])
    list_lu.sort()
    # bins of the landuse numbers
    # bins = [10,11,30, 60, 70,90, 100,110,120,122,130,140,150,152,160,180,210]
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

    # Create Piechart autopct='%1.2f',lambda pct: func(pct, data)
    elif(x=="Pie"):
        counts = Counter(list_lu)
        keys = counts.keys()
        values = counts.values()
        colours = ["goldenrod","navajowhite","yellowgreen","darkgoldenrod",
            "forestgreen","olive","limegreen","lime", "green","coral","gold",
            "olivedrab","black", "blue","darkseagreen","lightskyblue"]

        fig, ax = plt.subplots()
        data = [float(v) for v in values]
        wedges, texts, autotexts = ax.pie(data, labels=None,autopct='%1.2f', colors = colours)
        ax.legend(wedges, keys, title = "Landuse types", loc="left", bbox_to_anchor=(1, 0.8))
        #plt.setp(autotexts)
        ax.set_title("Landuses resting points (Threshold: Speed < Median)")
        fig.subplots_adjust(left=0.0125)
        plt.show()

def main():
    """
    Main function calling the other functions.
    """
    # IMPORTANT: Specify a path your data directory!
    data_dir = os.path.join("C:\\","Users","janni","OneDrive","Desktop","data")

    if(os.path.isdir(data_dir)):
        print("Very good! You have chosen a valid directory!")
        # load the point shapefile of the white-fronted goose manually!
        # access the active layer
        point_layer = iface.activeLayer()
        if not point_layer:
            print("Shape file failed to load!")
        else:
            # fn of landuse raster
            raster_fn = os.path.join(data_dir,"Eurasia_Landcover.tif")
            # rlayer = iface.addRasterLayer(raster_fn, 'Landuse')
            # specify path to legend of landuse
            landuse_legend_fn = os.path.join(data_dir,'Eurasia_Landcover_Legend.csv')

            # fn of the resting points shapefile
            in_shape_fn = os.path.join(data_dir,"lowSpeed.shp")

            # fn of the new shapefile including resting points and landuse identifier
            out_shape_fn = os.path.join(data_dir,"lowSpeedLanduseID.shp")

            # 1
            # INPUT: fn of the resting points
            # OUTPUT: fn of the new shapefile including resting points and landuse identifier
            # RASTERCOPY: fn of the landuse raster
            if(QgsProject.instance().mapLayersByName('lowSpeedLanduseID')==[]):
                processing.run("qgis:rastersampling",
                {'COLUMN_PREFIX' : 'LanduseNr_',
                'INPUT' : in_shape_fn,
                'OUTPUT' : out_shape_fn,
                'RASTERCOPY' : raster_fn})
                updated_shapefile = iface.addVectorLayer(out_shape_fn, '', 'ogr')
            else:
                updated_shapefile = QgsProject.instance().mapLayersByName('lowSpeedLanduseID')[0]
            print("-----------1-------------finished!")
            #2
            convertIdFloatToInt(updated_shapefile)
            print("-----------2-------------finished!")
            #3
            legend = preProcessLegend(landuse_legend_fn)
            print("-----------3-------------finished!")
            #4
            convertIdToName(legend,updated_shapefile)
            print("-----------4-------------finished!")
            #5
            plotLandUse(updated_shapefile,"Pie")
            print("-----------5-------------finished!")
            print("DONE! :)")
    else:
        iface.messageBar().pushMessage("Error", "The directory does not exist. Please change data_dir in the code",level = 1)
        print("Please specify a valid directory in the main function of Code_Extraction.py!")

main()
