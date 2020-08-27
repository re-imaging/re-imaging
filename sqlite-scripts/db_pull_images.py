import subprocess
import os
import sqlite3
import random

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

open_images = True

db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"

db = sqlite3.connect(db_path)
c = db.cursor()

sql = '''
    SELECT image_ids, caption, fignum
    FROM captions
    WHERE caption LIKE ?
    LIMIT 2000
    '''

term = "network architecture"
# c.execute(sql, ("%monte carlo%",))
c.execute(sql, ("%"+term+"%",))
rows = c.fetchall()

print("number of rows:",len(rows))
# print(rows[:3])

# random.shuffle(rows)

files = []
for image_ids, caption, fignum in rows:
    # print(image_ids, cat, created)
    if image_ids is not None:
        if "\|" in image_ids:
            # print("splitting string:",image_ids)
            ids = image_ids.split("\|")
            for id in ids:
                # print(id)
                files.append(id)
        else:
            files.append(image_ids)

# files = [str(x[0]) + ".jpg" for x in rows[:]]
print("total number of results:", len(files))

if open_images:
    os.chdir("/mnt/hd2/images/all")

    cmd = ["feh"]
    for file in files:
        cmd.append(file + ".jpg")
    # print(cmd)

    # for row in rows:
    #     print("fignum:",row[2])
    #     print("caption:",row[1])

    subprocess.run(cmd)
