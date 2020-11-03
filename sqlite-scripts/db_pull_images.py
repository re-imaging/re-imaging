import subprocess
import os
import sqlite3
import random

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import shlex

open_images = False
make_montage = True

db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"

db = sqlite3.connect(db_path)
c = db.cursor()

# sql = '''
#     SELECT image_ids, caption, fignum
#     FROM captions
#     WHERE caption LIKE ?
#     LIMIT 2000
#     '''

sql = '''
    SELECT id, creator, filename
    FROM images
    WHERE creator LIKE ?
    '''

# term = "network architecture"

term = "Photoshop"
# c.execute(sql, ("%monte carlo%",))
c.execute(sql, ("%"+term+"%",))
rows = c.fetchall()

print("number of rows:",len(rows))
# print(rows[:3])

# random.shuffle(rows)

# random.seed(4)
# random.shuffle(rows)

files = []
for image_ids, caption, fignum in rows[:64]:
    # print(image_ids, cat, created)
    if image_ids is not None:
        if type(image_ids) is not int:
            if "\|" in image_ids:
                # print("splitting string:",image_ids)
                ids = image_ids.split("\|")
                for id in ids:
                    # print(id)
                    files.append(id)
            else:
                files.append(image_ids)
        else:
            files.append(image_ids)

# files = [str(x[0]) + ".jpg" for x in rows[:]]
print("total number of results:", len(files))

if open_images:
    os.chdir("/mnt/hd2/images/all")

    cmd = ["feh"]
    for file in files:
        cmd.append(str(file) + ".jpg")
    # print(cmd)

    # for row in rows:
    #     print("fignum:",row[2])
    #     print("caption:",row[1])

    subprocess.run(cmd)


if make_montage:

    name = "montage_search_{}".format(term)
    outputname = ["/home/rte/documentation/data-samples/" + name + ".jpg"]

    prearg = shlex.split("-colorspace CMYK")

    arguments = shlex.split("-colorspace sRGB -background white -alpha background -geometry 240x240+2+2 -tile 8x")
    # call the montage command and parse list of files and arguments
    filelist = []
    for file in files:
        # filelist.append(str(file) + ".jpg")
        filelist.append("/mnt/hd2/images/all/" + str(file) + '.jpg[0]')


    montage_cmd = ["montage"] + prearg + filelist + arguments + outputname

    result = subprocess.Popen(montage_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = result.communicate()
    print(out)
    print(err)
    print("subprocess finished")
    print("-" * 40)
