#!/usr/bin/env python
# coding: utf-8

# In[10]:


pip install pyshp


# In[11]:


import shapefile


# In[12]:


sf = shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp")


# In[13]:


with shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp") as shp:
    print(shp)


# In[14]:


shapes = sf.shapes()


# In[15]:


len(shapes)


# In[16]:


print(shapes)


# In[17]:


s = sf.shape(3)


# In[18]:


print(s)


# In[19]:


#/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.shp


# In[20]:


sfp = shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.shp")


# In[21]:


with shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp") as shp:
    print(shp)


# In[22]:


shapesP = sfp.shapes()


# In[23]:


len(shapesP)


# In[24]:


print(shapesP)


# In[25]:


pip install dbfread


# In[26]:


from dbfread import DBF


# In[27]:


#/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf
for record in DBF('/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf'):
    print(record)


# ## Only print coordinates

# In[28]:


table = DBF('/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf', load=True)


# In[29]:


print(table.records[1]['long'])


# In[30]:


for record in table:
    print(record['long'])
    print(record['lat'])


# In[31]:


len(table)


# ## Saving Coordinates in a list

# In[32]:


list_of_coords = []


# In[33]:


for record in table:
    list_of_coords.append((record['lat'],record['long']))


# In[34]:


print(list_of_coords)


# ## Calculating Boundig Box

# In[116]:


import numpy


# In[117]:


print(list_of_coords[0][0])


# In[118]:


print(list_of_coords[0][1])


# In[147]:


min_coord_X=list_of_coords[0][0]
min_coord_Y=list_of_coords[0][1]


# In[148]:


min_bounding_box=[]


# ## Calculating bottom left point

# In[149]:


for coord in list_of_coords:
    print(coord)
    x=coord[0]
    y=coord[1]
    if x < min_coord_X and y < min_coord_Y:
        min_coord_X=x
        min_coord_Y=y
min_bounding_box.append([min_coord_X, min_coord_Y])


# In[150]:


print(min_bounding_box)


# ## Calculating bottom left point
# 

# In[155]:


max_bounding_box=[]


# In[156]:


max_coord_X=list_of_coords[0][0]
max_coord_Y=list_of_coords[0][1]


# In[157]:


for coord in list_of_coords:
    print(coord)
    x=coord[0]
    y=coord[1]
    if x > max_coord_X and y > max_coord_Y:
        max_coord_X=x
        max_coord_Y=y
max_bounding_box.append([max_coord_X, max_coord_Y])


# In[158]:


print(max_bounding_box)


# In[ ]:




