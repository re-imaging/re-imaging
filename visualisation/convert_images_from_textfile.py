#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import argparse
import itertools
import subprocess
from subprocess import Popen, PIPE, TimeoutExpired
import os
import shlex
import time
import sys

import datetime

print(sys.argv)

# In[ ]:


import os
import signal
from time import monotonic as timer

from PIL import Image
import math


# In[ ]:


parser = argparse.ArgumentParser(description='Script for converting images from a textfile')

parser.add_argument('textfile', help='textfile to read from')
parser.add_argument('convert_path', help='path to destination folder')
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('--timeout', default=30, type=int, help='timeout for convert command (default: 30)')
parser.add_argument('--verbose', action='store_true', help='verbose output')
parser.add_argument('--missing', action='store_true', help='write missing output file: True/False')
parser.add_argument('--lowdensity', action='store_true', help='run convert without density action (default: False)')

# convert_path = "/home/rte/data/images/random/100k/test/"
# convert_path = sys.argv[2]

# textfile = "/home/rte/data/images/random/100k/filepaths.txt"
# textfile = sys.argv[1]

# start_line = 43806 -1
# start_line = int(sys.argv[3])

counter = 0
missing_count = 0

global args
args = parser.parse_args()

textfile = args.textfile
convert_path = args.convert_path
start_line = args.start_line

print("lowdensity",args.lowdensity)

if args.verbose:
    print("textfile:",textfile)
    print("convert_path:",convert_path)
    print("start_line:",start_line)
    print("missing:",args.missing)

# In[ ]:


start = time.time()

filepaths = []
image_ids = []

with open(textfile, "r") as f:
    lines = f.readlines()
    print(len(lines))
    print(lines[0])
for l in lines:
    substrings = l.rsplit(",", 1)
    filepaths.append(substrings[0].strip())
    image_ids.append(substrings[1].strip())

print("total filepaths:",len(filepaths))
print("total image_ids:",len(image_ids))

end = time.time()
print("finished loading filepaths")
print("time taken:", end - start)


# In[ ]:


print("*" * 20)
print("checking the first filepath and id:")
print(filepaths[start_line], image_ids[start_line])
print("*" * 20)


# In[ ]:


# arguments for convert
if args.lowdensity:
    prearg = shlex.split("-colorspace CMYK")
else:
    prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background -trim +repage -flatten -resize 512x512^>")

now = datetime.datetime.now()
now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logpath = convert_path + "error_log_" + now_string + ".txt"
missing_logpath = convert_path + "missing_log_" + now_string + ".txt"
print("logging errors to:",logpath)
print("logging missing files to:",missing_logpath)

# logpath = convert_path + "error_log_from_textfile.txt"

overall_start = time.time()

for image_id, filepath in zip(image_ids[start_line:], filepaths[start_line:]):

    start = time.time()

    if counter % 100 is 0 and args.verbose:
        print("*" * 20)
        print("counter:",counter)
        print("converting image:",start_line+counter)
        print("*" * 20)


    outputname = [convert_path + str(image_id) + ".jpg"]
    if args.verbose:
        print("filename:",filepath)
        print("image_id:",image_id)
        print("outputname:",outputname)

    # test if image is already in the folder
    # output_str = str(outputname[0])
    # print(output_str)
    if os.path.isfile(str(outputname[0])):
        if args.verbose:
            print("file already exists!:",outputname)
    else:
        missing_count += 1

        print("*" * 20)
        print("file doesn't exist, converting")
        # write file path to missing log
        if args.missing:
            f = open(missing_logpath, "a+")
            f.write(filepath + "," + image_id + "\n")
            f.close()
        # call the montage command and parse list of files and arguments
        convert_cmd = ["convert"] + prearg + [":" + filepath + "[0]"] + arguments + outputname
        print(convert_cmd)

        extension = filepath.rsplit(".", 1)[1]
        print(extension)

        # if extension.lower() == 'png':
        #     try:
        #         im = Image.open(filepath)
        #         size = im.size
        #         smallest_dim = size.index(min(size)) # find if x or y is smaller
        #         ratio = 513 / size[smallest_dim] # 513 because PIL resizes to 1 pixel less, not sure why
        #         x = math.floor(size[0] * ratio)
        #         y = math.floor(size[1] * ratio)
        #         im.thumbnail((x, y), Image.ANTIALIAS)
        #         im.save(str(outputname[0]), "JPEG")
        #     except IOError:
        #         print("error converting PNG")
        # # if not a PNG
        # else:
        if True:
            try:
                # subprocess.run(convert_cmd, timeout=args.timeout)
                child = subprocess.Popen(convert_cmd, universal_newlines=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output,error = child.communicate(timeout=args.timeout)
                if child.returncode != 0:
                    raise Exception("exception")
                    print("returncode:",child.returncode)
                    print("output:",output)
                    print("error:",error)

            except TimeoutExpired:

                child.kill()

                print("!" * 20)
                print("timeout --- logging problem file")
                print("filename:",filepath)
                print("image_id:",image_id)
                print("outputname:",outputname)
                f = open(logpath, "a+")
                f.write(filepath + "," + image_id + "\n")
                f.close()
                print("-" * 20)

                continue

            except Exception:
                print("!" * 20)
                print("output:",output)
                print("error:",error)
                print("-" * 20)

                print("Exception --- logging problem file")
                print("filename:",filepath)
                print("image_id:",image_id)
                print("outputname:",outputname)
                f = open(logpath, "a+")
                f.write(filepath + "," + image_id + "\n")
                f.close()
                print("-" * 20)

                continue

            except:
                print("!" * 40)
                print("Unexpected error:", sys.exc_info()[0])
            else:
                print("*** image converted ***")

    counter += 1

    if args.verbose:
        print("time elapsed: {:.4f}".format(time.time() - start))
        print("-" * 20)

print("finished converting!")
print("total number of items:",counter)
end = time.time()
print("total time taken:", end - overall_start)
print("number of missing files:",missing_count)


# In[ ]:
