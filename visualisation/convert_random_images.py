#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sqlite3
import random
import itertools
import subprocess
import os
import shlex
import time


# In[ ]:


# Here we import the sqlite3 database and create a cursor
db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"
db = sqlite3.connect(db_path)
c = db.cursor()


# In[ ]:


# test that we can fetch the pragma for each table

c.execute('PRAGMA TABLE_INFO({})'.format("metadata"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)


# In[ ]:


c.execute('PRAGMA TABLE_INFO({})'.format("images"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)


# In[ ]:


# set variables for automating process

targetCats = ["cs.CV", "stat.ML", "math.CT", "physics.med-ph", "math.AC"]

# targetDate = "2009-01-01"
targetDates = ["2006-01-01", "2009-01-01", "2012-01-01", "2015-01-01", "2018-01-01"]


# ### Get 100k random samples

# In[ ]:


sql = ('''
    SELECT images.id, images.path, images.filename, images.identifier, metadata.cat
    FROM images
    LEFT JOIN metadata ON images.identifier = metadata.identifier
    WHERE images.x != ''
    ORDER BY RANDOM()
    LIMIT 1000000
    ''')

c.execute(sql)
rows = c.fetchall()
print("total number of entries found:", len(rows))


# In[ ]:


# view a subset
for row in rows[:20]:
    print(row)


# ### convert random subset

# In[ ]:


convert_path = "/home/rte/data/images/random/1k/"

start = time.time()

targetSize = 512

filepaths = []

for row in rows:
    path = row[1] + '/' + row[2]
#     print(path)
    filepaths.append(path.replace('./','/home/rte/arXiv/src_all/'))

print("total number of filepaths: " + str(len(filepaths)))

# write list of image paths and IDs to file (for debugging purposes, mostly)

fname = convert_path + "filepaths.txt"
# print(fname)
f = open(fname, "w+")
for path, row in zip(filepaths, rows):
    f.write(path + "," + str(row[0]) + "\n")
f.close()

# arguments for convert
# convert -density 300 -colorspace CMYK [input]
# -colorspace sRGB -background white \
# -alpha background -trim +repage -resize 512x512^ [out].jpg
prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background     -trim +repage -flatten -resize 512x512^>")
# print(arguments)

# call convert for each image path
for row, f in zip(rows, filepaths):
#     print(row)
#     print(f)
    outputname = [convert_path + str(row[0]) + ".jpg"]

#     print("calling convert")
    # call the montage command and parse list of files and arguments
    convert_cmd = ["convert"] + prearg + [f + "[0]"] + arguments + outputname
#     print(convert_cmd)

    result = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = result.communicate()
#     print(out)
    print(err)

print("finished converting!")
end = time.time()
print("time taken:", end - start)
