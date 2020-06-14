import os, ogr, osr, datetime, math, gdal
from qgis.core import *
import qgis.utils
import numpy as np

# load the point shapefile manually!

# access the active layer
point_layer = iface.activeLayer()
if not point_layer:
    print("Shape file failed to load!")
else: print("Shape file loaded!")

#Add new colums to store time and Date
caps = point_layer.dataProvider().capabilities()
if caps & QgsVectorDataProvider.AddAttributes:
    # We require a String field
    res = point_layer.dataProvider().addAttributes(
        [QgsField("Ob_Time", QVariant.String),\
        QgsField("Ob_Date", QVariant.String),\
        QgsField("Distance", QVariant.Double)])
        
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



# Initiate a variable to hold the date and time values extracted from shape file
updates_time = {}
updates_date={}
for feat in point_layer.getFeatures():
    # Get the date time value from the gpx
    date_time = feat['timestamp']
    date_time_obj = datetime.datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S')
    time = date_time_obj.strftime("%H:%M:%S")
    date = date_time_obj.strftime("%Y:%m:%d")
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

#Calculate the distance between two points 
#Count the number of features in the shape file


no_feat=point_layer.featureCount()

point_layer.selectByExpression("\"tag_ident\"=72413")
#Store UTM East and North coordinates in to lists
L_north=[]
L_east=[]
L_ID=[]


for feat in point_layer.getFeatures():
    east=feat['utm_east']
    north=feat['utm_north']
    L_north.append(north)
    L_east.append(east)
    L_ID.append(feat.id())

L_distance=[]
for j in range (0,(no_feat-1)):
    if j==0:
        distance=0
    else:
        D_north=(L_north[j]-L_north[j-1])**2
        D_East=(L_east[j]-L_east[j-1])**2
        distance=math.sqrt(D_north+D_East)
        L_distance.append(distance)
print ('Done')
print(L_distance[50])
