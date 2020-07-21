import gdal
import ogr
import os
import osr

from qgis.core import *
from qgis.gui import *
import qgis.utils


################################################## PATHS
# Step 1.1: Create a data directory
data_dir = os.path.join("C:\\","Users","janni","OneDrive","Desktop","data")

# Step 1.2: Create a path to goose track shapefile
in_vect = os.path.join(data_dir, 'points.shp')

# Step 1.3: Create a path to land cover raster file
in_rast = os.path.join(data_dir, 'Eurasia_Landcover.tif')

# Step 1.4: Create a path to an empty vector output file
out_vect = os.path.join(data_dir, 'transform_point.shp')

################################################## OPEN SOURCES - RASTER AND VECTOR + PRINT SPATIAL REFERENCE
# Step 2.1: Open the raster data source in Python3 and print its spatial reference information
rast_data_source = gdal.Open(in_rast)
rast_spatial_reference = rast_data_source.GetProjection()
print("The raster's spatial reference is:", rast_spatial_reference)

# Step 2.2: Import the correct driver into the module *to be able to read or write* the vector file
driver = ogr.GetDriverByName('ESRI Shapefile')

# Step 2.3: Open the vector data source in Python3 and check to see if shapefile is found by the code
# Note: 0 in Line 43 means 'read-only' and 1 would mean 'writeable'
vect_data_source = driver.Open(in_vect, 0)

# Step 2.4: Check if 'vect_data_source' was opened correctly through the input vector path
# Note: The term 'None' means 'if not found by the code' and the conditional statement ensures that errors won't occur
if vect_data_source is None:
    print('Could not open %s' % (in_vect))

# Step 2.5: You've loaded the vector data source, now create a layer for the contents pane with GetLayer() function
vect_layer = vect_data_source.GetLayer()

# Step 2.6: Now that the layer has been created, print its spatial reference information
vect_spatial_reference = vect_layer.GetSpatialRef()
print("The vector's spatial reference is:", vect_spatial_reference)

################################################## SPATIAL REFERENCE TRANSFORMATION
# Step 3.1: Create an OSR object of the raster file's spatial reference information
rast_sr_object = osr.SpatialReference(rast_spatial_reference)

# Step 3.2: Transform the GPX track shapefile projection to be the same as the raster file projection
transform_point_sr = osr.CoordinateTransformation(vect_spatial_reference, rast_sr_object)

################################################## DELETE OUTPUT FILE IF EXISTS + POPULATE OUTPUT DATA SOURCE
# Step 4.1: In case the empty output file was previously present, we must check and delete it *avoids error*
# Note: The driver was previously loaded as variable 'driver' and can be reused
if os.path.exists(out_vect):
    print('Output file exists, deleting...')
    driver.DeleteDataSource(out_vect)

# Step 4.2: Use the 'ESRI Shapefile' driver to create a new data source inside the empty vector output file
out_data_source = driver.CreateDataSource(out_vect)

# Step 4.3: Check if 'out_data_source' created a data source in the empty vector output file
# Note: The term 'None' means 'if not found by the code' and the conditional statement ensures that errors won't occur
if out_data_source is None:
    print('Could not create %s' % (out_vect))

################################################## CREATE SHAPEFILE LAYER WITH NEW PROJECTION
# Step 5.1: Create shapefile layer with the spatial reference of the raster file
out_vect_layer = out_data_source.CreateLayer('transform_point', rast_sr_object, ogr.wkbPoint)

# Step 5.2: Run a function that creates fields inside the table of the output vector file
out_vect_layer.CreateFields(vect_layer.schema)

# Step 5.3: Create a variable that produces a layer definition for the output file
out_defn = out_vect_layer.GetLayerDefn()

# Step 5.4: Create a variable that produces features through the layer definition of the output file
out_feat = ogr.Feature(out_defn)

# *Step 5.5: Create a loop that goes over every feature in the layer and changes the spatial reference

for in_feat in vect_layer:
    geom = in_feat.geometry()
    geom.Transform(transform_point_sr)
    out_feat.SetGeometry(geom)

    # Add a loop inside the loop to include the attributes in the new file
    for i in range(in_feat.GetFieldCount()):
        value = in_feat.GetField(i)
        out_feat.SetField(i, value)
    out_vect_layer.CreateFeature(out_feat)

################################################## DELETE OUTPUT DATA SOURCE
# Step 6.1: Delete output data source *to ensure multiple outputs are not produced so errors are avoid*
del out_data_source

iface.addVectorLayer(out_vect, '', 'ogr')
print('Job finished!')
