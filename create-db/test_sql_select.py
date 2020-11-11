import subprocess
import os
import sqlite3

db_path = "/home/rte/data/db/arxiv_db_images.sqlite3"

db = sqlite3.connect(db_path)
c = db.cursor()

version = 3

# first attempt, doesn't work so well
if version == 0:
    sql = '''
        SELECT path, filename
        FROM images
        WHERE identifier = ?
        '''
    c.execute(sql, ("1608.06451",))
    rows = c.fetchall()

    print("number of rows:",len(rows))

    files = []

    for r in rows:
        files.append("/".join(r))

    print(files[1])
    os.chdir("/home/rte/arXiv/src_all/")

    for file in files:
        subprocess.run(["xdg-open", file])

# open images based on identifier match
if version == 1:
    sql = '''
        SELECT id
        FROM images
        WHERE identifier = ?
        '''
    c.execute(sql, ("1608.06451",))
    rows = c.fetchall()

    print("number of rows:",len(rows))

    files = [str(x[0]) + ".jpg" for x in rows]
    print(files)
    os.chdir("/mnt/hd2/images/all")

    cmd = ["feh"]
    for file in files:
        cmd.append(file)
    print(cmd)

    # for file in files:
    subprocess.run(cmd)

# grab captions and show images
if version == 2:
    sql = '''
        SELECT "image_ids", caption, fignum
        FROM captions
        WHERE identifier = ?
        '''

    c.execute(sql, ("quant-ph0606026",))
    rows = c.fetchall()

    print("number of rows:",len(rows))

    files = [str(x[0]) + ".jpg" for x in rows]
    print(files)
    os.chdir("/mnt/hd2/images/all")

    cmd = ["feh"]
    for file in files:
        cmd.append(file)
    print(cmd)

    for row in rows:
        print("fignum:",row[2])
        print("caption:",row[1])

    subprocess.run(cmd)

# grab captions and show images where caption matches search
if version == 3:
    sql = '''
        SELECT "image_ids", caption, fignum
        FROM captions
        WHERE caption LIKE "%network architecture%"
        LIMIT 200
        '''

    c.execute(sql, ())
    rows = c.fetchall()

    print("number of rows:",len(rows))

    files = [str(x[0]) + ".jpg" for x in rows]
    print(files)
    os.chdir("/mnt/hd2/images/all")

    cmd = ["feh"]
    for file in files:
        cmd.append(file)
    print(cmd)

    for row in rows:
        print("fignum:",row[2])
        print("caption:",row[1])

    subprocess.run(cmd)

# check where image-id != null but no filenames
if version == 4:
    # sql = '''
    #     SELECT "image_ids", caption, fignum, identifier, filenames
    #     FROM captions
    #     WHERE "image_ids" IS NOT NULL AND filenames == ''
    #     '''

    sql = '''
        SELECT "image_ids", caption, fignum, identifier, filenames
        FROM captions
        WHERE "image_ids" IS NULL AND filenames != ''
        '''

    c.execute(sql, )
    rows = c.fetchall()

    print("number of rows:",len(rows))

    files = [str(x[0]) + ".jpg" for x in rows]
    # print(files)
    os.chdir("/mnt/hd2/images/all")

    # cmd = ["feh"]
    # for file in files:
    #     cmd.append(file)
    # print(cmd)

    last_identifier = ''

    for row in rows:
        if (last_identifier == row[3]) is False:
            # print("identifier:",row[3])
            # print("fignum:",row[2])
            # print("caption:",row[1])
            print(row[3])
            last_identifier = row[3]
    # subprocess.run(cmd)
