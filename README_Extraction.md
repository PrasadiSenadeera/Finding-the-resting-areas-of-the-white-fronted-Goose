## Migratory patterns of white-fronted goose in northern Europe
## Please update this if you change to the code.

### To use this code, manually load the shapefile into the QGIS interface

### This code includes,
**09.07.2020 - Add field prepared for Landuse Name and Nr(Jannis)**
- Extract landuse nr of the raster into the point shapefile
- Function for a first plot of landuse distribution
- Function containing preprocess of landuse legend
- First try on converting landuse nr to landuse label (Doesn't work yet)

**10.07.2020 - Add Label and improving plots (Jannis)**
- Conversion of float landuse identifier to int (new field)
- Conversion of int landuse identifier using legend to label (new field, String)
- Improved histogram plot
- Created pie chart of landuses
