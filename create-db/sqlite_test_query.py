import sqlite3

db = sqlite3.connect('testdb')

cursor = db.cursor()
cursor.execute('''SELECT id, identifier, name, cat FROM metadata''')
for row in cursor:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} : {1}, {2}, {3}'.format(row[0], row[1], row[2], row[3]))
