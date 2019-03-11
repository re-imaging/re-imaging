import sqlite3
# import pandas as pd

table_name = "metadata"

try:
    # create a database in RAM
    # db = sqlite3.connect(':memory:')
    # creates or opens a file database
    db = sqlite3.connect('arxiv_db.sqlite3')

    # get cursor object
    c = db.cursor()

    # c.execute('''
    #     CREATE TABLE metadata(id INTEGER PRIMARY KEY, identifier TEXT, created TEXT, cat TEXT, authors TEXT, title TEXT, abstract TEXT, licence TEXT)
    # ''')

    # c.execute('''
    #     INSERT INTO metadata(identifier, name, cat)
    #     VALUES(?,?,?)''', ('0101', 'some title', 'math'))
    # print('first entry inserted')
    #
    # c.execute('''
    #     INSERT INTO metadata(identifier, name, cat)
    #     VALUES(?,?,?)''', ('9901', 'a different title', 'cs'))
    # print('second entry inserted')

    # db.commit()

    c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
    info = c.fetchall()

    print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
    for col in info:
        print(col)



except Exception as e:
    # Roll back any change if something goes wrong
    db.rollback()
    raise e
finally:
    # Close the db connection
    db.close()
