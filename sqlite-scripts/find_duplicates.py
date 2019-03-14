import sqlite3

db_path = "/home/rte/data/db/arxiv_db_dup.sqlite3"

db = sqlite3.connect(db_path)
c = db.cursor()

print("finding duplicates")

# this command gets all the category totals in order (combined categories)
# c.execute('''
#     SELECT cat, COUNT(cat)
#     FROM metadata
#     GROUP BY cat
#     HAVING COUNT(cat) >= 1
#     ORDER BY COUNT(cat)
#     ''')

# query database for how many duplicate identifiers are in dataset
c.execute('''
    SELECT identifier, COUNT(identifier)
    FROM metadata
    GROUP BY identifier
    HAVING COUNT(identifier) > 1
    ''')

# check for how many entries on each created date
# c.execute('''
#     SELECT identifier, created, COUNT(created)
#     FROM metadata
#     GROUP BY created
#     HAVING COUNT(created) > 20
#     ''')

rows = c.fetchall()

for row in rows:
    print(row)

c.close()
db.close()
