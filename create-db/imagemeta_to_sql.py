import datetime
import os
import sys
import sqlite3
import argparse
import subprocess

import time

parser = argparse.ArgumentParser(description='Script for getting image metadata and writing to database')

# parser.add_argument('paths_file', help='textfile to read image paths from')
parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('images_path', help="path to folder of images")
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-t', '--timing', action='store_true', help='timing output')

global args
args = parser.parse_args()

table_name = "images"
startline = 0

now = datetime.datetime.now()
now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logpath = "error_log_" + now_string + ".txt"


def get_metadata(path, id, _c, field):
    if args.timing:
        start = time.time()

    command = ["exiftool"] + ["-T"] + ["-" + field] + [path]
    # print(command)

    sql = ('''
    UPDATE images
    SET creator = ?
    WHERE id = ?
    ''')

    if args.timing:
        end = time.time()
        print("time taken prior to subprocess:",end-start)
        start = time.time()

    creator = ""

    try:
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
        # p = subprocess.run(['identify', '-ping', '-format', '%w %h %m %b', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # out, err = p.communicate()
        # errcode = p.returncode

        # print("output:",out.decode('utf-8'))
        # print("error:",err)
        # print("errcode:",errcode)

        creator = p.rsplit("\n")[0]
        # creator = ""
        # for r in results:
        #     if r.startswith("Creator"):
        #         creator = p[34:]
        #         break
        print("creator:",creator)
        print("id:",id)
        print("*" * 20)

    except subprocess.TimeoutExpired:
        print("timeout")
    except UnicodeDecodeError:
        creator = ""
    # finally:

    if args.timing:
        end = time.time()
        print("time taken for exiftool:",end-start)
        start = time.time()

    if creator != "":
        _c.execute(sql, (creator, id))

    if args.timing:
        end = time.time()
        print("time taken for db update:",end-start)
        start = time.time()

    return 0

def main():

    if args.timing:
        start = time.time()

    count = startline

    db = sqlite3.connect(args.db_path)
    c = db.cursor()

    sql = ('''
    SELECT id, path, filename
    FROM images
    ''')

    c.execute(sql, )

    rows = c.fetchall()
    print("number of entries:",len(rows))

    if args.timing:
        end = time.time()
        print("time taken to load entries:",end-start)
        start = time.time()

    os.chdir(args.images_path)

    c.execute("BEGIN TRANSACTION;")

    # loop over all images, processing one at a time
    for row in rows[startline:]:
        if args.timing:
            start = time.time()

        # print(row)
        id = row[0]
        print(id)
        path = row[1] + "/" + row[2]
        # print("count:",count)
        # print(path)
        filename = row[2]
        n = filename.lower()
        print(filename)

        if n.endswith(('.eps', '.ps', 'pstex', '.epsf', '.epsi')):
            if args.verbose: print("PS")
            get_metadata(path, id, c, "Creator")
        elif n.endswith(('.png')):
            if args.verbose: print("PNG")
            get_metadata(path, id, c, "Software")
        elif n.endswith(('.pdf')):
            if args.verbose: print("PDF")
            get_metadata(path, id, c, "Creator")
        elif n.endswith(('.jpg', 'jpeg')):
            if args.verbose: print("JPG")
            get_metadata(path, id, c, "Software")
        elif n.endswith(('.gif')):
            if args.verbose: print("GIF")
            get_metadata(path, id, c, "Comment")
        elif n.endswith(('.svg')):
            if args.verbose: print("SVG")
            get_metadata(path, id, c, "Desc")
        else:
            print("***** Extension not recognised, exiting *****")
            with open(logpath, "a+") as f:
                f.write(filename + "," + id + "\n")
            sys.exit()

        count += 1

        # write database every so often to protect against crashes etc
        if count % 1000 == 0 and count != 0:
            db.commit()

            if args.timing:
                end = time.time()
                print("time taken for db commit:",end-start)
                start = time.time()

            c.execute("BEGIN TRANSACTION;")

    print("done, cleaning up db")

    db.commit()
    c.close()
    db.close()

if __name__ == "__main__":
    main()
