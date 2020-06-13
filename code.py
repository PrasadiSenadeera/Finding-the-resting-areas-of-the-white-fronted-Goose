import os
from qgis.core import *
import qgis.utils
import datetime
import gdal
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
        [QgsField("Ob_Time", QVariant.String),QgsField("Ob_Date", QVariant.String)])
        
# Update to propagate the changes  
point_layer.updateFields()

# Get the index of the new field
field_name_i_search1 = 'Ob_Time'
field_name_i_search2 = 'Ob_Date'
fields = point_layer.dataProvider().fields()

indexT = 0
indexD = 0

for field in point_layer.fields():
    if field.name() == field_name_i_search1:
        break
    indexT += 1
print(indexT)

for field in point_layer.fields():
    if field.name() == field_name_i_search2:
        break
    indexD += 1
print(indexD)

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
    updates_time[feat.id()] = {indexT:time}
    updates_date[feat.id()] = {indexD:date}
#print(updates)

# Use the created dictionary to update the field for all features
point_layer.dataProvider().changeAttributeValues(updates_time)
point_layer.dataProvider().changeAttributeValues(updates_date)
# Update to propagate the changes  
point_layer.updateFields()



print ('Done')
