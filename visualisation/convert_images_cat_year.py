#!/usr/bin/env python
# coding: utf-8

# In[67]:


import sqlite3
import random
import itertools
import subprocess
import os
import shlex


# In[68]:


# Here we import the sqlite3 database and create a cursor
db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"
db = sqlite3.connect(db_path)
c = db.cursor()


# In[69]:


# test that we can fetch the pragma for each table

c.execute('PRAGMA TABLE_INFO({})'.format("metadata"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)


# In[70]:


c.execute('PRAGMA TABLE_INFO({})'.format("images"))
info = c.fetchall()

print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
for col in info:
    print(col)


# In[71]:


# set variables for automating process

targetCats = ["cs.CV", "stat.ML", "math.CT", "physics.med-ph", "math.AC"]

# targetDate = "2009-01-01"
targetDates = ["2006-01-01", "2009-01-01", "2012-01-01", "2015-01-01", "2018-01-01"]


# In[72]:


# cat_it = 0
# date_it = 0


# In[81]:


for targetCat in targetCats:
    for targetDate in targetDates:
        print(targetDate + "---" + targetCat)


# ### Loop starts here 

# In[87]:


for targetCat in targetCats:
    for targetDate in targetDates:
        print(targetDate + "---" + targetCat)

        targetY = int(targetDate[:4])
        targetM = int(targetDate[5:7])
        targetYM = targetDate[:7]

        targetSize = 512

        # check if the folder exists
        # if it does, it means we have likely already run these commands
        # if not, create it

        convert_path = "/home/rte/data/images/cat/" + targetCat + "/" + str(targetY) + "/"
        print("trying to save to: " + convert_path)
        exists = False

        if os.path.isdir(convert_path):
            print("folder exists! stopping process")
            exists = True
#             break
        else:
            print("creating directory...")
            try:
#                 print("testing")
                os.makedirs(convert_path)
            except OSError:
                print("Failed to create directory: " + convert_path)
            else:
                print("Successfully created the directory: " + convert_path)
                
        # Get each image entry for a category/year

        if exists is False:
            sql = ('''
                SELECT images.id, images.path, images.filename, images.identifier, metadata.created
                FROM images
                LEFT JOIN metadata ON images.identifier = metadata.identifier
                WHERE metadata.created BETWEEN date(?) AND date(?, "start of month","+12 month","-1 day")
                AND images.x != ''
                AND substr(trim(metadata.cat),1,instr(trim(metadata.cat)||' ',' ')-1) = ?
                ''')

            c.execute(sql, (targetDate, targetDate, targetCat))
            rows = c.fetchall()
            print("total number of data rows: " + str(len(rows)))

            # put all the filepaths into a list

            filepaths = []

            for row in rows:
                path = row[1] + '/' + row[2]
            #     print(path)
                filepaths.append(path.replace('./','/home/rte/arXiv/src_all/'))

            print("total number of filepaths: " + str(len(filepaths)))


            # write list of images to file (for debugging purposes, mostly)

            fname = convert_path + str(targetY) + "_" + targetCat + ".txt"
            print(fname)
            f = open(fname, "w+")
            for path, row in zip(filepaths, rows):
                f.write(path + "," + str(row[0]) + "\n")
            f.close()

            
            # arguments for convert
            arguments = shlex.split("-colorspace sRGB -units PixelsPerInch -density 300 -background white -alpha off -resize " + str(targetSize) + "^")
            # print(arguments)

            # call convert for each image path
            for row, f in zip(rows, filepaths):
            #     print(row)
            #     print(f)
                outputname = [convert_path + str(row[0]) + ".jpg"]

                print("calling convert")
                # call the montage command and parse list of files and arguments
                convert_cmd = ["convert"] + [f + "[0]"] + arguments + outputname
            #     print(convert_cmd)

                result = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = result.communicate()
                print(out)
                print(err)

#                 print("subprocess finished")
#                 print("-" * 40)
            print("finished converting year/category")

print("script finished!")

