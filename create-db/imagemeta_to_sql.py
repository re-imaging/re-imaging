import datetime
import os
import sys
import sqlite3
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Script for getting image metadata and writing to database')

# parser.add_argument('paths_file', help='textfile to read image paths from')
parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

global args
args = parser.parse_args()

table_name = "images"
startline = 0

def get_pdfinfo(path):
    command = ["exiftool"] + ["-Creator"] + [path]
    try:
        p = subprocess.run(command, stdout=subprocess.PIPE, timeout=30).stdout.decode('utf-8')
# p = subprocess.run(['identify', '-ping', '-format', '%w %h %m %b', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
        print(p)
        results = p.rsplit("\n")
        # print(results[0])
        creator = ""
        for r in results:
            if r.startswith("Creator"):
                creator = p[34:]
            # break
        print("creator:",creator)
        print("*" * 20)

    except subprocess.TimeoutExpired:
        print("timeout")

    # sys.exit()
    # return creator

def main():

    count = 0

    db = sqlite3.connect(args.db_path)
    c = db.cursor()

    sql = ('''
    SELECT id, path, filename
    FROM images
    ''')

    db.create_function("reverse", 1, lambda s: s[::-1])

    c.execute(sql, )

    rows = c.fetchall()
    # for row in rows:
        # print(row)
    print(len(rows))

    os.chdir("/home/rte/arXiv/src_all/")

    # loop over all images, processing one at a time
    for row in rows:
        # c.execute("BEGIN TRANSACTION")
        print(row)
        id = row[1]
        path = row[1] + "/" + row[2]
        print(path)
        filename = row[2]
        n = filename.lower()
        print(filename)
        if n.endswith(('.eps', '.ps', 'pstex', '.epsf', '.epsi')):
            print("PS")

        elif n.endswith(('.png')):
            print("PNG")
        elif n.endswith(('.pdf')):
            print("PDF")
            get_pdfinfo(path)
        elif n.endswith(('.jpg', 'jpeg')):
            print("JPG")
        elif n.endswith(('.gif')):
            print("GIF")
        elif n.endswith(('.svg')):
            print("SVG")
        else:
            print("***** SOMETHING ELSE *****")
            # sys.exit()




        # c.execute("COMMIT;") # probably not this
        # db.commit()


    # write count when crashing etc.

    # try:
    #     subprocess.run(convert_cmd, timeout=30)
    # except subprocess.TimeoutExpired:

    # PDF
    #  pdfinfo {} | grep -i "creator" | cut -c 17-

    # GIF
    # exiftool -Comment {} | cut -c 35-

    # PS
    # "*.*ps*" | xargs -d '\n' -l1 -I {} exiftool -Creator {} | cut -c 35-

    # JPG
    # exiftool -Software {} | cut -c 35-

    # SVG
    # exiftool -f -Desc | cut -c

    # PNG
    # exiftool -Software {} | cut -c 35-

    '''
    BEGIN TRANSACTION;

    UPDATE image
    SET creator = ?
    WHERE id = ?
    '''

    # do in transactions, 1k at a time? or 10k?

if __name__ == "__main__":
    main()
