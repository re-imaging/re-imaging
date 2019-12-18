import sqlite3
import random
import itertools
import subprocess
import os
import shlex
import time
import sys

import shutil

# script to grab all file paths from SQLite database and attempts to convert each to a smaller jpg
#
# WARNING: Use with caution, can fill disk
# NB: this is also single-thread and slow, recommended to use convert_images_from_textfile_threaded.py instead

print(sys.argv, len(sys.argv))

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

# ### Get all image rows from the database
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

# start_line = 43806 -1
start_line = int(sys.argv[1]) - 1

# view a subset
print("first rows")
for row in rows[start_line:start_line + 5]:
    print(row)

# ### Write text file with all filepaths and IDs
print("organising data into variables")

filepaths = []
image_ids = []

for row in rows:
    path = row[1] + '/' + row[2]
#     print(path)
    filepaths.append(path.replace('./','/home/rte/arXiv/src_all/'))
    image_ids.append(row[0])
print("total filepaths:", len(filepaths))
print("total ids:", len(image_ids))

print("*" * 20)
print("checking the first filepath and id:")
print(filepaths[start_line], image_ids[start_line])
print("*" * 20)

# write list of image paths and IDs to file (for debugging purposes, mostly)
'''
print("writing text file")

fname = "filepaths_all_images.txt"
# print(fname)
f = open(fname, "w+")
for path, row in zip(filepaths, rows):
    f.write(path + "," + str(row[0]) + "\n")
f.close()
'''

# ### convert all images

# convert_path = "/home/rte/data/images/all/"
convert_path = "/mnt/hd2/images/all/"
print("converting to:",convert_path)

source_path = convert_path
dest_path = "/mnt/hd2/images/all/"

space_limit = 20

# arguments for convert
prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background -trim +repage -flatten -resize 512x512^>")

logpath = "/home/rte/re-imaging/visualisation/error_log.txt"

overall_start = time.time()

counter = start_line

for image_id, filepath in zip(image_ids[start_line:], filepaths[start_line:]):

    start = time.time()

    if counter % 100 is 0:
        print("*" * 20)
        print("counter:",counter)
        print("process has been running for:", time.time() - overall_start)
        print("*" * 20)
    '''
    # this code only really relevant if moving to boot disk
    # run a counter only every now and then
    if counter % 1000 is 0:
        # move all image files to HD
        print("moving files")
        files = os.listdir(source_path)
        for f in files:
            shutil.move(source_path+f, dest_path)

        # make sure we have disk space free
        total, used, free = shutil.disk_usage("/")
        print("checking disk space:")
#         print("Total: %d GB" % (total // (2**30)))
#         print("Used: %d GB" % (used // (2**30)))
        print("Free: %d GB" % (free // (2**30)))
        if free // (2**30) > space_limit:
            print("enough space free, continuing")

        # if not enough disk space, sleep for a while
        while free // (2**30) < 20:
            total, used, free = shutil.disk_usage("/")
            print("Free: %d GB" % (free // (2**30)))
            print("not enough disk space remaining...sleeping 60 seconds")
            time.sleep(60)
#     a more forceful way to quit?
#     if free // (2**30) > 5:
#         sys.exit("not enough disk space remaining")
    '''

#     print("filename:",filepath)
    outputname = [convert_path + str(image_id) + ".jpg"]
#     print("outputname:",outputname)

    # call the montage command and parse list of files and arguments
    convert_cmd = ["convert"] + prearg + [filepath + "[0]"] + arguments + outputname
#     print(convert_cmd)

    try:
        subprocess.run(convert_cmd, timeout=30)
    except subprocess.TimeoutExpired:
        print("!" * 20)
        print("timeout --- logging problem file")
        print("id:",str(image_id))
        f = open(logpath, "a+")
        f.write(filepath + "," + str(image_id) + "\n")
        f.close()
        print("-" * 20)

        continue

    counter += 1

#     print("time elapsed: {:.2f}".format(time.time() - start))
#     print("-" * 20)

print("finished converting!")
print("total number of items:",counter)
end = time.time()
print("total time taken:", end - overall_start)
