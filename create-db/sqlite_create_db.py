# create an SQLite database with tables for metadata and images

import sqlite3

# db_path = "/home/rte/data/db/arxiv_db.sqlite3"
db_path = "/home/rte/data/db/test_db.sqlite3"

try:
    # create a database in RAM
    # db = sqlite3.connect(':memory:')
    # creates or opens a file database
    db = sqlite3.connect(db_path)

    # get cursor object and create metadata table
    c = db.cursor()
    c.execute('''
        CREATE TABLE metadata(id INTEGER PRIMARY KEY, identifier TEXT, created TEXT, \
        cat TEXT, authors TEXT, title TEXT, abstract TEXT, licence TEXT)
    ''')

    # create images table
    c.execute('''
        CREATE TABLE images (id INTEGER PRIMARY KEY, identifier TEXT, filename TEXT, \
        filesize INT, path TEXT, x INT, y INT, imageformat TEXT)
    ''')

    # for testing insertion

    # c.execute('''
    #     INSERT INTO metadata(identifier, name, cat)
    #     VALUES(?,?,?)''', ('0101', 'some title', 'math'))
    # print('first entry inserted')
    #
    # c.execute('''
    #     INSERT INTO metadata(identifier, name, cat)
    #     VALUES(?,?,?)''', ('9901', 'a different title', 'cs'))
    # print('second entry inserted')

    db.commit()

except Exception as e:
    # Roll back any change if something goes wrong
    db.rollback()
    raise e
finally:
    # Close the db connection
    db.close()
