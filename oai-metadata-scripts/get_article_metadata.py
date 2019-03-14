import sqlite3

db_path = "/home/rte/data/db/arxiv_db_dup.sqlite3"

db = sqlite3.connect(db_path)
c = db.cursor()

inputID = "1801.00001" # for testing purposes
# inputID = input("Enter an arXiv identifier: ")
print("searching for " + inputID)

c.execute('SELECT identifier, cat, created FROM metadata WHERE identifier=?', (inputID,))

rows = c.fetchall()

for row in rows:
    print(row)

c.close()
db.close()
