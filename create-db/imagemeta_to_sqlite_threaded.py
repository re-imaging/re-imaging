import datetime
import os
import sys
import sqlite3
import argparse
import subprocess
import concurrent.futures
from functools import partial
import itertools

import time

parser = argparse.ArgumentParser(description='Script for getting image metadata and writing to database')

# parser.add_argument('paths_file', help='textfile to read image paths from')
parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('images_path', help="path to folder of images")
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('-s', '--slice_size', default=2500, type=int, help='size of each slice to process (default: 2500)')
parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-t', '--timing', action='store_true', help='timing output')
parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify or create any files (default: False)")

global args
args = parser.parse_args()

table_name = "images"

db = sqlite3.connect(args.db_path)
c = db.cursor()

now = datetime.datetime.now()
now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logpath = "error_log_" + now_string + ".txt"


def get_metadata(row):

    if args.timing:
        start = time.time()

    id = row[0]
    # print("id:",id)
    path = row[1] + "/" + row[2]
    # print(path)
    filename = row[2]
    n = filename.lower()
    # print(filename)

    # test file extension and set field with appropriate metadata field
    if n.endswith(('.eps', '.ps', 'pstex', '.epsf', '.epsi')):
        field = "Creator"
    elif n.endswith(('.png')):
        field = "Software"
    elif n.endswith(('.pdf')):
        field = "Creator"
    elif n.endswith(('.jpg', 'jpeg')):
        field = "Software"
    elif n.endswith(('.gif')):
        field = "Comment"
    elif n.endswith(('.svg')):
        field = "Desc"
    else:
        print("***** Extension not recognised, exiting *****")
        with open(logpath, "a+") as f:
            f.write(filename + "," + id + "\n")
        sys.exit()

    command = ["exiftool"] + ["-T"] + ["-" + field] + [path]
    # print(command)

    creator = ""

    try:
        p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')
        # print(p)

        creator = p.rsplit("\n")[0]
        # print(creator)

    except subprocess.TimeoutExpired:
        print("timeout")
        return id, creator
    except UnicodeDecodeError:
        creator = ""
    except:
        with open(logpath, "a+") as f:
            f.write(filename + "," + id + "\n")
        return id, creator
    # finally:

    if args.timing:
        end = time.time()
        print("time taken for subprocess:",end-start)

    return id, creator


def main():

    if args.timing:
        start = time.time()

    # count = args.start_line

    sql = ('''
    SELECT id, path, filename
    FROM images
    ''')
    # if specific time ranges etc. are required, modify the above SQL, e.g.
    #     WHERE identifier LIKE '19%' OR identifier LIKE '20%'

    c.execute(sql, )

    rows = c.fetchall()
    print("number of entries:",len(rows))

    if args.timing:
        end = time.time()
        print("time taken to load entries:",end-start)
        start = time.time()

    os.chdir(args.images_path)

    c.execute("BEGIN TRANSACTION;")

    sql = ('''
    UPDATE images
    SET creator = ?
    WHERE id = ?
    ''')

    # break work up into chunks so as to limit memory usage
    increment = args.slice_size
    slices = [i for i in range(args.start_line + increment, len(rows), increment)]
    slices.append(len(rows)) # add the total length at the end
    print("slices:",slices)
    slice_start = args.start_line

    for slice_end in slices:

        print("taking slice from",slice_start,"to",slice_end)
        data = rows[slice_start:slice_end]
        # sys.exit()

        if args.dryrun:
            pass
        else:
            print("running futures")
            starter = partial(get_metadata, logpath=logpath)
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as tp:
                for input, output in zip(data, tp.map(get_metadata, data)):
                    if args.verbose:
                        print("input:",input)
                        print("output:",output)

                    c.execute(sql, (output[1], output[0]))

                    # count += 1
                    # if count % 1000 == 0 and count != 0:

        # commit at the end of each slice
        print("input:",input)
        print("output:",output)
        print("committing to db")
        db.commit()
        c.execute("BEGIN TRANSACTION;")

        slice_start = slice_end

        print("finished running futures")

    print("done, cleaning up db")
    db.commit()
    c.close()
    db.close()

if __name__ == "__main__":
    main()
