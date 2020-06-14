## Implementing a python based algorithm to investigate the behavior of White-fronted geese during their migration routes

## Please update this if you change to the code.

### First load your shape file mannually to QGIS interface

### This code includes,
**13.06.2020 - created two new fields with date and time (Prasadi)**
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
 




