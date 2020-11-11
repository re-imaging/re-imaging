import os
import shlex
import subprocess

readfile = "/home/rte/arXiv/src_update/error_log_20200918_163124.txt"

filepaths = []
outputnames = []
lines = []
conversion_path = "/mnt/hd2/images/gimp_update/"

# with open(readfile, "r") as input:
#     lines = input.readlines()

lines = [line.rstrip('\n') for line in open(readfile)]

# print(lines)

for line in lines:
    # print(line)
    filepaths.append(line.split(',')[0])
    outputnames.append(line.rsplit(',', 2)[1])

# print(filepaths)
# print(outputnames)

for f, o in zip(filepaths, outputnames):

    print(f, o)
    gimp_cmd = shlex.split("gimp -i -b '(convert-to-jpeg \"" + f + "\" \"" + conversion_path + o + ".jpg\")' -b '(gimp-quit 0)'")

    print(gimp_cmd)
    subprocess.run(gimp_cmd, 60)
