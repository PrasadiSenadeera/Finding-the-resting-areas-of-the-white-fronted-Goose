import os
import ogr
import datetime
import math
import time
from qgis.core import *
from qgis.gui import *
import qgis.utils
import numpy as np
from matplotlib import pyplot as plt
import statistics

# This code computes and plots the speed of the goose per datapoint
# After that it splits the data based on a threshold into resting and flying points

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

def addTimeAndDateObs(layer):
    """
    Initiate a variable to hold the date and time values extracted from shape file and populate them.
        Parameters:
            layer: QGIS layer object
    """
    #Create field for storing time of observation
    newColumn (layer,"Ob_Time", QVariant.String)
    #Create field for storing date of observation
    newColumn (layer,"Ob_Date", QVariant.String)
    # Empty objects for storing the updates
    updates_time = {}
    updates_date = {}
    indexT=layer.fields().indexFromName('Ob_Time')
    indexD=layer.fields().indexFromName('Ob_Date')
    print("STARTING LOOP!")
    for feat in layer.getFeatures():
        # Get the date time value from the gpx
        date_time = feat['timestamp']
        date_time_obj = datetime.datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S')
        time = date_time_obj.strftime("%H:%M:%S")
        date = date_time_obj.strftime("%Y-%m-%d")
        # Update the empty fields in the shapefile
        updates_time[feat.id()] = {indexT:time}
        updates_date[feat.id()] = {indexD:date}
    #print(updates)

    # Use the created dictionary to update the field for all features
    layer.dataProvider().changeAttributeValues(updates_time)
    layer.dataProvider().changeAttributeValues(updates_date)
    # Update to propagate the changes
    layer.updateFields()
    print("Time and date fields populated.")

def addDistance(layer, tracks):
    """
    Calculate the distance between two points and add a field for that purpose.
        Parameters:
            layer: QGIS layer object
            tracks: List containing trackID of different geese
    """

    #Create field for store Distance
    newColumn (layer,"Distance", QVariant.Double)

    #Select seperate locations(points) of each route and save their properties in to lists
    for m in range(0,len(tracks)):
        #create empty lists to save UTM coordinates, track number, feature ID
        L_north=[]
        L_east=[]
        L_ID=[]
        L_distance=[]

        layer.selectByExpression(tracks[m], QgsVectorLayer.SetSelection)
        selection = layer.selectedFeatures()
        for feature in selection:
            east=feature['utm_east']
            north=feature['utm_north']
            L_north.append(north)
            L_east.append(east)
            L_ID.append(feature.id())

        #Calculate the euclidean distance between a point and its previous point
        for j in range (0,(len(L_north))):
            if j==0:
                distance=0
                L_distance.append(distance)
            else:
                D_north=(L_north[j]-L_north[j-1])**2
                D_East=(L_east[j]-L_east[j-1])**2
                distance=math.sqrt(D_north+D_East)
                L_distance.append(distance)

        #Update distances to a new field
        updates_distance={}
        for i in range (0,(len(L_north))):
            # Get the distance value from the gpx
            distance=L_distance[i]
            index=L_ID[i]

            # Update the empty fields in the shapefile
            indexDi=layer.fields().indexFromName('Distance')
            updates_distance[index] = {indexDi:distance}

        layer.dataProvider().changeAttributeValues(updates_distance)
        # Update to propagate the changes
        layer.updateFields()
        layer.removeSelection()

        L_north.clear()
        L_east.clear()
        L_ID.clear()
        L_distance.clear()

def calcTimeDiff(layer, tracks):
    """
    Calculate the time difference between two points and add a field for that purpose.
        Parameters:
            layer: QGIS layer object
            tracks: List containing trackID of different geese
    """

    # Check if field already exists
    if layer.fields().indexFromName("TimeDiff") == -1:
        #Create field to store TimeDifference
        newColumn (layer,"TimeDiff", QVariant.Double)

    #Create a list to store time values
    for m in range(0,len(tracks)):
        L_Datetime=[]
        L_ID=[]
        L_TimeDiff=[]

        layer.selectByExpression(tracks[m], QgsVectorLayer.SetSelection)
        selection = layer.selectedFeatures()
        for feature in selection:
            Datetime=feature['timestamp']
            L_Datetime.append(Datetime)
            L_ID.append(feature.id())


        #Calculate time between a point and its previous point
        for j in range (0,(len(L_ID))):
            if j==0:
                TimeDiff=0
                L_TimeDiff.append(TimeDiff)
            else:
                To_time=datetime.datetime.strptime(L_Datetime[j],'%Y-%m-%d %H:%M:%S')
                From_time=datetime.datetime.strptime(L_Datetime[j-1],'%Y-%m-%d %H:%M:%S')
                TimeDiff=To_time-From_time

                value=TimeDiff.total_seconds()
                L_TimeDiff.append(value)
        #Update time difference to a new field

        updates_timeDiff={}
        for i in range (0,(len(L_TimeDiff))):
            # Get the distance value from the gpx
            TimeDiff=L_TimeDiff[i]
            index=L_ID[i]

            # Update the empty fields in the shapefile
            indexTimeDiff=layer.fields().indexFromName('TimeDiff')
            updates_timeDiff[index] = {indexTimeDiff:TimeDiff}

        layer.dataProvider().changeAttributeValues(updates_timeDiff)
        # Update to propagate the changes
        layer.updateFields()
        layer.removeSelection()

        L_Datetime.clear()
        L_ID.clear()
        L_TimeDiff.clear()

def calcSpeed(layer):
    """
    Calculate the speed between two points and store it into a new field.
        Parameters:
            layer: QGIS layer object
    """
    #Create new field to store speed
    newColumn (layer,"Speed", QVariant.Double)

    updates_speed={}
    for feat in layer.getFeatures():
        a=feat['Distance']
        b=feat['TimeDiff']

        if (a==0 or b==0) :
            speed=0
        else:
            speed=a/b/1000*3600
        index=feat.id()

        indexSpeed=layer.fields().indexFromName('Speed')
        updates_speed[index] = {indexSpeed:speed}

    layer.dataProvider().changeAttributeValues(updates_speed)
    layer.updateFields()
    layer.removeSelection()

def descriptiveStatisticsSpeed(layer):
    """
    Function for calculating basic statistics of the speed field.
        Parameters:
            layer: QGIS layer object
        Returns:
            Median
    """

    features = layer.getFeatures()
    list_speed = []
    # Iterate over features and add to a list
    for feature in features:
        list_speed.append(feature['Speed'])
    # calculate mean
    mean_speed = statistics.mean(list_speed)
    print("Average speed: {} km/h".format(mean_speed))
    # calculate median
    median_speed = statistics.mean(list_speed)
    print("Median of speed: {} km/h".format(median_speed))
    # calculate sd
    sd_speed = statistics.stdev(list_speed)
    print("Standard deviation of speed: {} km/h".format(sd_speed))
    # calculate Variance
    var_speed = statistics.variance(list_speed)
    print("Variance of speed: {} km/h".format(var_speed))
    # Create histogram
    plt.hist(list_speed,bins = 6500, facecolor = 'g')
    plt.xlim(0,1)
    plt.xlabel('Speed in km/h')
    plt.ylabel('Frequency')
    plt.title('Histogram of speed values')
    plt.grid(True)
    plt.show()
    return median_speed

def extractSlowPoints(layer, threshold,outfn):
    """
    Function for selecting points with speed value below a specified Threshold. Creates new shapefile for selected points.
        Parameters:
            layer: QGIS layer object
            threshold (double): Speed value determining the split
            outfn(String): path to new shapefile
    """
    # Feature selection using a threshold for speed
    layer.selectByExpression( "\"Speed\"< {}".format(threshold))
    print("Selection based on this value: {} km/h".format(threshold))
    selection = layer.selectedFeatures()
    # mark selection red in map
    iface.mapCanvas().setSelectionColor( QColor("red") )
    # specify filename
    fn = os.path.join(outfn,'lowSpeed.shp')
    writer = QgsVectorFileWriter.writeAsVectorFormat(layer, fn, 'utf-8', driverName='ESRI Shapefile', onlySelected=True)
    selected_layer = iface.addVectorLayer(fn, '', 'ogr')
    del(writer)

def main():
    """
    Main function calling the other functions.
    """
    # IMPORTANT: Specify a path to the new shapefile!
    data_dir = os.path.join("C:\\","Users","janni","OneDrive","Desktop","data")

    #Store route identification codes in to a list
    L_tracks=['"tag_ident"=72413','"tag_ident"=72417','"tag_ident"=73053','"tag_ident"=72364',\
    '"tag_ident"=73054','"tag_ident"=79694','"tag_ident"=79698']
    if(os.path.isdir(data_dir)):
        print("Very good! You have chosen a valid directory!")
        # load the point shapefile of the white-fronted goose manually!
        # access the active layer
        point_layer = iface.activeLayer()
        if not point_layer:
            print("Shape file failed to load!")
        else:
            # 1
            addTimeAndDateObs(point_layer)
            print("-----------1-------------finished!")
            # 2
            addDistance(point_layer, L_tracks)
            print("-----------2-------------finished!")
            # 3
            calcTimeDiff(point_layer, L_tracks)
            print("-----------3-------------finished!")
            # 4
            calcSpeed(point_layer)
            print("-----------4-------------finished!")
            # 5
            extractSlowPoints(point_layer,descriptiveStatisticsSpeed(point_layer),data_dir)
            print("-----------5-------------finished!")
            print('Done')
    else:
        iface.messageBar().pushMessage("Error", "The directory does not exist. Please change data_dir in the code",level = 1)
        print("Please specify a valid directory in the main function of Code_Speed.py!")
main()
