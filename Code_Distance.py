import os, ogr, datetime, math, time, csv, processing, statistics
from qgis.core import *
from qgis.gui import *
import qgis.utils
import numpy as np
from matplotlib import pyplot as plt
from collections import Counter

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
                distance=(math.sqrt(D_north+D_East))/1000
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

def Statistics(layer):
    Statistics=processing.run("qgis:basicstatisticsforfields",{'INPUT_LAYER':layer, 'FIELD_NAME':'Distance',\
    'OUTPUT_HTML_FILE':'TEMPORARY_OUTPUT'})
    Mean = Statistics["MEAN"]
    STD = Statistics["STD_DEV"]
    variance= math.sqrt(STD)
    #print(Mean,STD,variance)

    #Calculate the threshold value
    Threshold=Mean-variance
    #print(Threshold)

    # Create histogram
    features = layer.getFeatures()
    list_distance = []
    # Iterate over features and add to a list
    for feature in features:
        list_distance.append(feature['Distance'])
    '''
    plt.hist(list_distance,bins = 6500, facecolor = 'g')
    plt.xlim(0,15)
    plt.xlabel('Distance in km')
    plt.ylabel('Frequency')
    plt.title('Histogram of Distance values')
    plt.grid(True)
    plt.show()
    '''
    return Threshold


def extractPoints(layer,Threshold,dir):
    Selected_layer=layer.selectByExpression('"Distance"<{}'.format(Threshold), QgsVectorLayer.SetSelection)
    selection = layer.selectedFeatures()
    iface.mapCanvas().setSelectionColor( QColor("red") )
    if(os.path.isdir(dir)):
        fn = os.path.join(dir,'lowDistance.shp')
        writer = QgsVectorFileWriter.writeAsVectorFormat(layer, fn, 'utf-8', driverName='ESRI Shapefile', onlySelected=True)
        selected_layer = iface.addVectorLayer(fn, '', 'ogr')
        del(writer)
    else:
        print("No shapefile created: Please specify a correct directory!")  


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
    # bins of the landuse numbers
    # bins = [10,11,30, 60, 70,90, 100,110,120,122,130,140,150,152,160,180,210]
    if(x=="Hist"):
        # Create histogram
        plt.hist(list_lu, density = True, color="orange")
        plt.xlabel('Landuse type')
        plt.xticks(rotation = "vertical", size = "x-small", stretch =  'condensed')
        plt.ylabel('Frequency')
        plt.title('Histogram of landuses - resting points (Distance below mean-variance)')
        plt.grid(True)
        plt.tight_layout()
        plt.subplots_adjust(bottom = 0.45)
        plt.show()

    # Create Piechart autopct='%1.2f',lambda pct: func(pct, data)
    elif(x=="Pie"):
        counts = Counter(list_lu)
        keys = counts.keys()
        values = counts.values()
        fig, ax = plt.subplots()
        data = [float(v) for v in values]
        wedges, texts, autotexts = ax.pie(data, labels=None,autopct='%1.2f')
        ax.legend(wedges, keys, title = "Landuse types", loc="left", bbox_to_anchor=(1, 0.8))
        #plt.setp(autotexts)
        ax.set_title("Landuses resting points (Threshold: Distance < [Mean-Variance])")
        fig.subplots_adjust(left=0.0125)
        plt.show()

def main():
    """
    Main function calling the other functions.
    """
    # IMPORTANT: Specify a path to the new shapefile!
    data_dir = os.path.join("F:\\","Master","Semester 2","Academic","Python","Project output")
    

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
            print("-----------Created Date and Time objects-------------")
            # 2
            addDistance(point_layer, L_tracks)
            print("-----------Distances calculation finished-------------")
            # 3
            extractPoints(point_layer,Statistics(point_layer),data_dir)
            print("-----------Low distance points extracted and save to a new shapefile-------------")
            print('Done')

            raster_fn = os.path.join(data_dir,"Eurasia_Landcover.tif")
            landuse_legend_fn = os.path.join(data_dir,'Eurasia_Landcover_Legend.csv')
            in_shape_fn = os.path.join(data_dir,"lowDistance.shp")
            out_shape_fn = os.path.join(data_dir,"lowDistanceLanduseID.shp")

    
        if(QgsProject.instance().mapLayersByName('lowDistanceLanduseID')==[]):
            processing.run("qgis:rastersampling",
            {'COLUMN_PREFIX' : 'LanduseNr_',
            'INPUT' : in_shape_fn,
            'OUTPUT' : out_shape_fn,
            'RASTERCOPY' : raster_fn})
            updated_shapefile = iface.addVectorLayer(out_shape_fn, '', 'ogr')
        else:
            updated_shapefile = QgsProject.instance().mapLayersByName('lowDistanceLanduseID')[0]
        #2
        convertIdFloatToInt(updated_shapefile)
        #3
        legend = preProcessLegend(landuse_legend_fn)
        #4
        convertIdToName(legend,updated_shapefile)
        #5
        plotLandUse(updated_shapefile,"Pie")
        print("-----------finished!-------------")
        print("DONE! :)")
    else:
        iface.messageBar().pushMessage("Error", "The directory does not exist. Please change data_dir in the code",level = 1)
        print("Please specify a valid directory in the main function of Code_Distance.py!")
main()       
