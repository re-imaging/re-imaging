#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import sqlite3

import itertools
import subprocess
from subprocess import Popen, PIPE, TimeoutExpired
import os
import shlex
import time
import sys

print(sys.argv)


# In[ ]:


import os
import signal
from time import monotonic as timer


# Here we import the sqlite3 database and create a cursor
db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"
db = sqlite3.connect(db_path)
c = db.cursor()

# test that we can fetch the pragma for each table

c.execute('PRAGMA TABLE_INFO({})'.format("metadata"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)

c.execute('PRAGMA TABLE_INFO({})'.format("images"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)

# Get all images from the database
print("getting rows from database...")
sql = ('''
    SELECT images.id, images.path, images.filename, images.identifier, metadata.cat
    FROM images
    LEFT JOIN metadata ON images.identifier = metadata.identifier
    WHERE images.x != ''
    ''')

c.execute(sql)
rows = c.fetchall()
print("total number of rows:",len(rows))


convert_path = "/mnt/hd2/"
# convert_path = sys,argv[3]

textfile = "/home/rte/data/images/random/100k/filepaths.txt"
# textfile = sys.argv[1]

start_line = 43806 -1
# start_line = sys.argv[2] - 1

counter = 0


# In[ ]:


start = time.time()

filepaths = []
image_ids = []

with open(textfile, "r") as f:
    lines = f.readlines()
    print(len(lines))
    print(lines[0])
for l in lines:
    substrings = l.split(",")
    filepaths.append(substrings[0].strip())
    image_ids.append(substrings[1].strip())

print("total filepaths:",len(filepaths))
print("total image_ids:",len(image_ids))

end = time.time()
print("finished loading filepaths")
print("time taken:", end - start)


# In[ ]:


print("*" * 20)
print("checking the first filepath and id:")
print(filepaths[start_line], image_ids[start_line])
print("*" * 20)


# In[ ]:


# arguments for convert
prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background     -trim +repage -flatten -resize 512x512^> -verbose")

logpath = convert_path + "error_log.txt"

overall_start = time.time()

for image_id, filepath in zip(image_ids[start_line:], filepaths[start_line:]):

    start = time.time()

    if counter % 10 is 0:
        print("*" * 20)
        print("counter:",counter)
        print("converting image:",start_line+counter)
        print("*" * 20)

    print("filename:",filepath)
    outputname = [convert_path + str(image_id) + ".jpg"]
    print("outputname:",outputname)

    # call the montage command and parse list of files and arguments
    convert_cmd = ["convert"] + prearg + [filepath + "[0]"] + arguments + outputname
#     print(convert_cmd)

    try:
        subprocess.run(convert_cmd, timeout=30)
    except subprocess.TimeoutExpired:
        print("!" * 20)
        print("timeout --- logging problem file")
        f = open(logpath, "a+")
        f.write(filepath + "," + str(image_id) + "\n")
        f.close()
        print("-" * 20)

        continue

    counter += 1

    print("time elapsed: {:.2f}".format(time.time() - start))
    print("-" * 20)

print("finished converting!")
print("total number of items:",counter)
end = time.time()
print("total time taken:", end - overall_start)


# In[ ]: