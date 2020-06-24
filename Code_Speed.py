import os, ogr, osr, datetime, math, gdal, time
from qgis.core import *
from qgis.gui import *
import qgis.utils
import numpy as np

# load the point shapefile manually!
#############################################################Create two new colums to store Time and Date ############################################################################
# access the active layer
point_layer = iface.activeLayer()
if not point_layer:
    print("Shape file failed to load!")
else: print("Shape file loaded!")

#Add new colums

def newColumn (layer,FieldName,DataType):
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.AddAttributes:
        res = point_layer.dataProvider().addAttributes([QgsField(FieldName,DataType)])
# Update to propagate the changes
    point_layer.updateFields()


# Get the index of the new field
def getIndex(layer,Field_name):
    index=0
    fields = layer.dataProvider().fields()
    for field in layer.fields():
        if field.name() == Field_name:
            break
        index += 1
    return index

# Check if field already exists
if  point_layer.fields().indexFromName("Ob_Time") == -1:
    #Create field for store Date
    newColumn (point_layer,"Ob_Time", QVariant.String)

# Check if field already exists
if point_layer.fields().indexFromName("Ob_Date") == -1:
    #Create field for store Date
    newColumn (point_layer,"Ob_Date", QVariant.String)

# Initiate a variable to hold the date and time values extracted from shape file
updates_time = {}
updates_date={}
for feat in point_layer.getFeatures():
    # Get the date time value from the gpx
    date_time = feat['timestamp']
    date_time_obj = datetime.datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S')
    time = date_time_obj.strftime("%H:%M:%S")
    date = date_time_obj.strftime("%Y-%m-%d")

    # Update the empty fields in the shapefile
    indexT=getIndex(point_layer,'Ob_Time')
    indexD=getIndex(point_layer,'Ob_Date')
    updates_time[feat.id()] = {indexT:time}
    updates_date[feat.id()] = {indexD:date}
#print(updates)

# Use the created dictionary to update the field for all features
point_layer.dataProvider().changeAttributeValues(updates_time)
point_layer.dataProvider().changeAttributeValues(updates_date)
# Update to propagate the changes
point_layer.updateFields()

#####################################################Calculate the distance between two points###################################################

#Store route identification codes in to a list
L_tracks=['"tag_ident"=72413','"tag_ident"=72417','"tag_ident"=73053','"tag_ident"=72364',\
'"tag_ident"=73054','"tag_ident"=79694','"tag_ident"=79698']


# Check if field already exists
if point_layer.fields().indexFromName("Distance") == -1:
    #Create field for store Distance
    newColumn (point_layer,"Distance", QVariant.Double)

#create empty lists to save UTM coordinates, track number, feature ID

#Select seperate locations(points) of each route and save their properties in to lists
for m in range(0,len(L_tracks)):
    L_north=[]
    L_east=[]
    L_ID=[]
    L_distance=[]

    point_layer.selectByExpression(L_tracks[m], QgsVectorLayer.SetSelection)
    selection = point_layer.selectedFeatures()
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

    # for check the values
    #print(L_north[0],L_east[0],L_ID[0],L_distance[0])
    #print(L_north[1],L_east[1],L_ID[1],L_distance[1])
    #print(L_north[2],L_east[2],L_ID[2],L_distance[2])

    #Update distances to a new field

    updates_distance={}
    for i in range (0,(len(L_north))):
        # Get the distance value from the gpx
        distance=L_distance[i]
        index=L_ID[i]

        # Update the empty fields in the shapefile
        indexDi=getIndex(point_layer,'Distance')
        updates_distance[index] = {indexDi:distance}

    point_layer.dataProvider().changeAttributeValues(updates_distance)
    # Update to propagate the changes
    point_layer.updateFields()
    point_layer.removeSelection()

    L_north.clear()
    L_east.clear()
    L_ID.clear()
    L_distance.clear()

#############################################Calculate time difference########################################

# Check if field already exists
if point_layer.fields().indexFromName("TimeDiff") == -1:
    #Create field to store TimeDifference
    newColumn (point_layer,"TimeDiff", QVariant.Double)

#Create a list to store time values
for m in range(0,len(L_tracks)):
    L_Datetime=[]
    L_ID=[]
    L_TimeDiff=[]

    point_layer.selectByExpression(L_tracks[m], QgsVectorLayer.SetSelection)
    selection = point_layer.selectedFeatures()
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

    # for check the values

    #print(L_Datetime[0],L_TimeDiff[0])
    #print(L_Datetime[1],L_TimeDiff[1])
    #print(L_Datetime[2],L_TimeDiff[2])


    #Update time difference to a new field

    updates_timeDiff={}
    for i in range (0,(len(L_TimeDiff))):
        # Get the distance value from the gpx
        TimeDiff=L_TimeDiff[i]
        index=L_ID[i]

        # Update the empty fields in the shapefile
        indexTimeDiff=getIndex(point_layer,'TimeDiff')
        updates_timeDiff[index] = {indexTimeDiff:TimeDiff}

    point_layer.dataProvider().changeAttributeValues(updates_timeDiff)
    # Update to propagate the changes
    point_layer.updateFields()
    point_layer.removeSelection()

    L_Datetime.clear()
    L_ID.clear()
    L_TimeDiff.clear()

##############################################Calculate speed##################################################

# Check if field already exists
if point_layer.fields().indexFromName("Speed") == -1:
    #Create new field to store speed
    newColumn (point_layer,"Speed", QVariant.Double)

updates_speed={}
for feat in point_layer.getFeatures():
    a=feat['Distance']
    b=feat['TimeDiff']

    if (a==0 or b==0) :
        speed=0
    else:
        speed=a/b/1000*3600
    index=feat.id()

    indexSpeed=getIndex(point_layer,'Speed')
    updates_speed[index] = {indexSpeed:speed}

point_layer.dataProvider().changeAttributeValues(updates_speed)
point_layer.updateFields()
point_layer.removeSelection()


print('Done')
