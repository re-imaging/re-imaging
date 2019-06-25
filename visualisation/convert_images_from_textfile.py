#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import itertools
from subprocess import Popen, PIPE, TimeoutExpired
import os
import shlex
import time
import sys

print(sys.argv)


# In[ ]:


import os
import signal
from time import monotonic as timer


# In[ ]:


convert_path = "/home/rte/data/images/random/100k/test/"
# convert_path = sys,argv[3]

textfile = "/home/rte/data/images/random/100k/filepaths.txt"
# textfile = sys.argv[1]

start_line = 43806 -1
# start_line = sys.argv[2] - 1
counter = 0


# In[ ]:


start = time.time()

filepaths = []
image_ids = []

with open(textfile, "r") as f:
    lines = f.readlines()
    print(len(lines))
    print(lines[0])
for l in lines:
    substrings = l.split(",")
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
prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background     -trim +repage -flatten -resize 512x512^> -verbose")

logpath = convert_path + "error_log.txt"

start = time.time()


for image_id, filepath in zip(image_ids[start_line:], filepaths[start_line:]):
    
    if counter % 10 is 0:
        print("*" * 20)
        print("counter:",counter)
        print("converting image:",start_line+counter)
        print("*" * 20)
        
    outputname = [convert_path + str(image_id) + ".jpg"]
    print("outputname:",outputname)

    # call the montage command and parse list of files and arguments
    convert_cmd = ["convert"] + prearg + [filepath + "[0]"] + arguments + outputname
    print(convert_cmd)

    try:
        subprocess.run(convert_cmd, timeout=5)
    except subprocess.TimeoutExpired:
        f = open(logpath, "a+")
        f.write(filepath + "," + image_id + "\n")
        f.close()
        continue

    counter += 1
    
    print("time elapsed: {:.2f}".format(time.time() - start))
    
print("finished converting!")
end = time.time()
print("total time taken:", end - start)


# In[ ]:




