#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install pyshp


# In[2]:


import shapefile


# In[6]:


sf = shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp")


# In[8]:


with shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp") as shp:
    print(shp)


# In[9]:


shapes = sf.shapes()


# In[10]:


len(shapes)


# In[11]:


print(shapes)


# In[13]:


s = sf.shape(3)


# In[14]:


print(s)


# In[15]:


#/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.shp


# In[17]:


sfp = shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.shp")


# In[18]:


with shapefile.Reader("/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/lines.shp") as shp:
    print(shp)


# In[19]:


shapesP = sfp.shapes()


# In[20]:


len(shapesP)


# In[21]:


print(shapesP)


# In[25]:


pip install dbfread


# In[26]:


from dbfread import DBF


# In[28]:


#/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf
for record in DBF('/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf'):
    print(record)


# ## Only print coordinates

# In[29]:


table = DBF('/Users/ilka/Documents/Uni/Master/PIG/Daten/goose/White-fronted goose full year tracks 2006-2010 Alterra IWWR/points.dbf', load=True)


# In[30]:


print(table.records[1]['long'])


# In[33]:


for record in table:
    print(record['long'])
    print(record['lat'])


# In[34]:


len(table)


# ## Saving Coordinates in a list

# In[48]:


list_of_coords = []


# In[50]:


for record in table:
    list_of_coords.append((record['lat'],record['long']))


# In[51]:


print(list_of_coords)


# ## Calculating Boundig Box

# In[39]:


pip install planar


# In[40]:


from planar import BoundingBox


# In[53]:


bbox = BoundingBox(list_of_coords)


# In[54]:


print(bbox)


# In[ ]:




