## Migratory patterns of white-fronted goose in northern Europe

## Please update this if you change to the code.

### To use this code, manually load the shapefile into the QGIS interface

### This code includes,
**13.06.2020 - Create two new fields with date and time (Prasadi)**
  * Access the active layer
  * Add new two colums to store time and Date
  * Initiate a variable to hold the date and time values extracted from shape file and store extracted variables to a dictionary
  * Use the created dictionary to update the field for all features (Now there are two new colums for date and time seperately)

**14.06.2020 - Calculate the distance between two points (Prasadi)**
 * Store route identification codes in to a list
 * Create empty lists to store UTM coordinates, track number and feature ID
 * Select locations(points) of each route seperately and save their properties in to lists
 * Calculate the euclidean distance between a point and its previous point
 * Update distances to a new field
 * Update to propagate the changes
 * Clear lists before next iteration
  
**19.06.2020 - Minor change (Jannis)**
 * Check existence of fields before adding new fields

**02.07.2020 - Calculate descriptive statistics of Distance and threshold (Prasadi)**
 * Threshold=Mean-Variance
 
**02.07.2020 - Extract values based on Distance (Prasadi)**

**Create new shapefile containing just low distance points (Jannis)**

**Extract landuse at selected locations (Prasadi)**

**Show results using a Pie chart and a Histogram (Prasadi)**

**19.07.2020 Changed colours of pie chart (Jannis)**
 * Unification

