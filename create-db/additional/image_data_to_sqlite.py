import glob
import os
import sqlite3
import subprocess
import scandir
# import binascii
# from PIL import Image

# verbose = True
verbose = False

# src_path = "/home/rte/arXiv/src_50/"
src_path = "/home/rte/arXiv/src_all/"
db_path = "/home/rte/data/db/arxiv_db_test.sqlite3"

count = 0

db = sqlite3.connect(db_path)
c = db.cursor()

def insert_image(_identifier, _filename, _filesize, _path, _x, _y, _imageformat):
    # c = db.cursor()
    c.execute("INSERT INTO images (identifier, filename, filesize, path, x, y, imageformat) \
    VALUES (?, ?, ?, ?, ?, ?, ?)", \
    (_identifier, _filename, _filesize, _path, _x, _y, _imageformat))
    # c.close()

print(os.getcwd())
os.chdir(src_path)
print(os.getcwd())

for root, dirs, files in scandir.walk("."):
    for name in files:
        try:
            filename = os.path.join(root, name)
            # print(filename)
            n = name.lower()
            # print("root: " + root)
            spl = root.split("/")
            if len(spl) > 1:
                article_name = root.split("/")[2]
            else:
                article_name = ""
            # print("article: " + article_name)

            # check to see if the lowercase filename matches common extensions
            # also check to make sure it isn't an image extracted from a PDF
            # and that it also isn't a PDF that was provided as PDF-only article (ARTICLE-IDXXX.pdf)
            if n.endswith(('.png', '.eps', '.pdf', '.ps', '.jpg', 'jpeg', 'pstex', '.gif', '.svg', '.epsf'))\
            and 'pdf_image' not in n\
            and name != (article_name + ".pdf"):
                print(name)
                count += 1

                # print out the count at regular intervals
                if (count % 10 == 0):
                    print("---------- count: " + str(count))

                # filesize = os.stat(filename).st_size

                # p = subprocess.check_output(['identify', filename]).decode('utf-8')
                # args = '-format "%w %h %m"'
                p = subprocess.run(['identify', '-ping', '-format', '%w %h %m %b', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
                # print(p)
                split_p = p.split(" ")

                # cmd = ['identify', filename]
                # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                #
                # o, e = proc.communicate()
                #
                # print('Output: ' + o.decode('ascii'))
                # print('Error: '  + e.decode('ascii'))
                # print('code: ' + str(proc.returncode))

                # im = Image.open(filename)

                x = split_p[0]
                y = split_p[1]
                imageformat = split_p[2]
                filesize = split_p[3]

                if(verbose):
                    print(article_name)
                    print(name)
                    print(filesize)
                    print(root)
                    print(x)
                    print(y)
                    print(imageformat)
                    print("-" * 20)
                # imagemode = im.mode
                # print("imageformat: " + imageformat)
                # print("imagemode: " + imagemode)

                insert_image(article_name, name, filesize, root, x, y, imageformat)

                if(count >= 200):
                    break

        except Exception as e:
            print(e)
            continue
            # raise e
        except KeyboardInterrupt:
            c.close()
            db.commit()
            db.close()
            print("total count: " + str(count))
            raise
        # finally:
        #     c.close()
        #     db.commit()
        #     db.close()

c.close()
db.commit()
db.close()
print("total count: " + str(count))
