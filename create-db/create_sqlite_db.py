# create an SQLite database with tables for metadata, images, and captions

import sqlite3
import os

db_path = os.path.expanduser("~/data/db/arxiv_db.sqlite3")

try:
    # creates or opens a file database
    db = sqlite3.connect(db_path)

    # get cursor object and create metadata table
    c = db.cursor()

    # create metadata table
    c.execute('''
        CREATE TABLE metadata(id INTEGER PRIMARY KEY, identifier TEXT, created TEXT, \
        cat TEXT, authors TEXT, title TEXT, abstract TEXT, licence TEXT)
    ''')

    # create images table
    c.execute('''
        CREATE TABLE images (id INTEGER PRIMARY KEY, identifier TEXT, filename TEXT, \
        filesize INT, path TEXT, x INT, y INT, imageformat TEXT, creator TEXT)
    ''')

    # create captions table
    c.execute('''
        CREATE TABLE "captions" ("id" INTEGER, "identifier" TEXT, "tex" TEXT, \
        "fignum" TEXT, "caption" TEXT, "label" TEXT, "filenames" TEXT, "image_ids" TEXT, PRIMARY KEY("id"))
    ''')

    db.commit()

except Exception as e:
    # Roll back any change if something goes wrong
    db.rollback()
    raise e
finally:
    # Close the db connection
    db.close()
