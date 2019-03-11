import sqlite3
try:
    # create a database in RAM
    # db = sqlite3.connect(':memory:')
    # creates or opens a file database
    db = sqlite3.connect('testdb')

    # get cursor object
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE metadata(id INTEGER PRIMARY KEY, identifier TEXT, name TEXT, cat TEXT)
    ''')

    cursor.execute('''
        INSERT INTO metadata(identifier, name, cat)
        VALUES(?,?,?)''', ('0101', 'some title', 'math'))
    print('first entry inserted')

    cursor.execute('''
        INSERT INTO metadata(identifier, name, cat)
        VALUES(?,?,?)''', ('9901', 'a different title', 'cs'))
    print('second entry inserted')

    db.commit()

except Exception as e:
    # Roll back any change if something goes wrong
    db.rollback()
    raise e
finally:
    # Close the db connection
    db.close()
