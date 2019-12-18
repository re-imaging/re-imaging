import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Script for writing a text file with all paths from SQLite database')
parser.add_argument('database', help='path to database')
parser.add_argument('textfile', help='textfile to write file paths to')

global args
args = parser.parse_args()

# Here we import the sqlite3 database and create a cursor
# db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"
db_path = args.database
db = sqlite3.connect(db_path)
c = db.cursor()

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

# write list of image paths and IDs to file (for debugging purposes, mostly)
print("writing text file")

# fname = "filepaths_all_images_test.txt"
fname = args.textfile

# print(fname)
f = open(fname, "w+")
for path, row in zip(filepaths, rows):
    f.write(path + "," + str(row[0]) + "\n")
f.close()
