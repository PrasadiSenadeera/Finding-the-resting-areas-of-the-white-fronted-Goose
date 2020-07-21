import gdal
import ogr
import os
import osr

################################################## DATA DIRECTORY, PATHS AND EMPTY OUTPUT FILE
# Step 1.1: Create a data directory
data_dir = os.path.join("C:\\","Users","janni","OneDrive","Desktop","data")

# Step 1.2: Create a path to goose track shapefile
in_vect = os.path.join(data_dir, 'transform_point.shp')

# Step 1.3: Create a path to land cover raster file
in_rast = os.path.join(data_dir, 'Eurasia_Landcover.tif')

# Step 1.4: Create a path to an empty raster output file
out_rast = os.path.join(data_dir, 'clipped_Eurasia_Landcover.tif')

################################################## OPEN RASTER AND TRANSLATE COORDINATES TO RASTER INDICES
# Step 2.1: Open the raster file
rast_ds = gdal.Open(in_rast)

print("Projection of Raster dataset: {}".format(rast_ds.GetProjection()))

# Step 2.2: Translate coordinates to raster indices
geoTrans = rast_ds.GetGeoTransform()
inv_geoTrans = gdal.InvGeoTransform(geoTrans)

################################################## GET GPS TRACK DRIVER, OPEN VECTOR LAYER AND CALCULATE EXTENT
# Step 3.1: Get the correct driver for the gps track
vect_driver = ogr.GetDriverByName('ESRI Shapefile')

# Step 3.2: Open the vector data source in Python3 and check to see if shapefile is found by the code
# Note: 0 means read-only. 1 means writeable,
vect_ds = ogr.Open(in_vect, 0)

# Step 3.3: Check if 'vect_data_source' was opened correctly through the input vector path
# Note: The term 'None' means 'if not found by the code' and the conditional statement ensures that errors won't occur
if vect_ds is None:
    print('Could not open %s' % (in_vect))

# Step 3.4: You've loaded the vector data source, now create a layer for the contents pane with GetLayer() function
shape_layer = vect_ds.GetLayer(0)
if not shape_layer:
    print("Shapefile failed to load!")
else:
    print("Shapefile loaded!")

extent = shape_layer.GetExtent()
print('The shape layer extent is: ', extent)

print("Projection of Vector dataset: {}".format(shape_layer.GetSpatialRef()))

################################################## DETERMINE BUFFER SIZE AND COORDINATES FOR CLIP
# Step 4.1: Decide on the size of the buffer around the track
buffer = 1000

# Step 4.2: Calculate values for min-1,2 and max-1,2
x1, y1 = gdal.ApplyGeoTransform(inv_geoTrans, extent[0] - buffer, extent[2] - buffer)
x2, y2 = gdal.ApplyGeoTransform(inv_geoTrans, extent[1] + buffer, extent[3] + buffer)

# Step 4.3: Print the column numbers and then round the indices (especially when not using a buffer)
print('The column numbers are: ', x1, y1, x2, y2)
x1 = int(round(x1))
y1 = int(round(y1))
x2 = int(round(x2))
y2 = int(round(y2))

# Step 4.4: Calculate how many rows and columns the ranges cover and print output
# Note: y-indices increase from top to bottom
out_columns = x2 - x1
out_rows = y1 - y2
print('The output raster extent will be: ', out_columns, out_rows)

################################################## SIGNAL RASTER DRIVER, CREATE DATA SOURCE
# Step 5.1: Signal the correct GeoTiff driver
rast_driver = gdal.GetDriverByName('GTiff')

# Step 5.2: Create an output data source (clipped size) with output raster, columns, rows and # bands
# Note: 1 means one band
# Note: Rasters can be overwritten, output file cannot be deleted if already exists
out_ds = rast_driver.Create(out_rast, out_columns, out_rows, 1)

# Step 5.3: Set projection for rast_data_source, create a list from geoTrans variable and set GeoTransform() to it
# Note: Geotransform can remain the same, except the y origin!
out_ds.SetProjection(rast_ds.GetProjection())
out_geoTrans = list(geoTrans)

out_geoTrans[0] = extent[0] - buffer
out_geoTrans[3] = extent[3] + buffer

out_ds.SetGeoTransform(out_geoTrans)

# Step 5.4: Get data from the source raster and write to the new one
in_band = rast_ds.GetRasterBand(1)
out_band = out_ds.GetRasterBand(1)

# ReadAsArray() for only the parts needed, flush cache and print action complete!
data = in_band.ReadAsArray(x1, y2, out_columns, out_rows)
out_band.WriteArray(data)
out_ds.FlushCache()

print('Actions complete!')
