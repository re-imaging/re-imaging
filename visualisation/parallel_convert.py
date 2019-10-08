import argparse
import itertools
import subprocess
from subprocess import Popen, PIPE, TimeoutExpired
import os
import signal
import shlex
import time
import sys
import datetime
from multiprocessing import Pool, cpu_count

parser = argparse.ArgumentParser(description='Script for converting images from a textfile')

parser.add_argument('textfile', help='textfile to read from')
parser.add_argument('convert_path', help='path to destination folder')
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('--timeout', default=30, type=int, help='timeout for convert command (default: 30)')
# parser.add_argument('--missing', action='store_true', help='write missing output file: True/False')
parser.add_argument('--lowdensity', action='store_true', help='run convert with lower density (dpi) (default: False)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

global args
args = parser.parse_args()

if args.lowdensity:
    prearg = shlex.split("-density 72 -colorspace CMYK")
else:
    prearg = shlex.split("-density 300 -colorspace CMYK")
arguments = shlex.split("-colorspace sRGB -background white -alpha background -trim +repage -flatten -resize 512x512^>")

# handle Ctrl+C - this doesn't seem to work so well?
def signal_handler(signal, frame):
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# this function converts an image
# with excessive error handling in case the Imagemagick convert call fails
def convert(filepath, outputname, logpath):
    # print(argin)
    # filepath = argin[0]
    # outputname = argin[1]
    print("filename:",filepath)
    print("outputname:",outputname)

    # is there an easier way to reference this?
    global prearg
    global arguments

    image_id = os.path.basename(outputname[0])

    convert_cmd = ["convert"] + prearg + [":" + filepath + "[0]"] + arguments + outputname
    extension = filepath.rsplit(".", 1)[1]
    # print(extension)
    try:
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
        # print("image_id:",image_id)
        print("outputname:",outputname)
        f = open(logpath, "a+")
        f.write(filepath + "," + image_id + "\n")
        f.close()
        print("-" * 20)

    except Exception:
        print("!" * 20)
        print("output:",output)
        print("error:",error)
        print("-" * 20)

        print("Exception --- logging problem file")
        print("filename:",filepath)
        # print("image_id:",image_id)
        print("outputname:",outputname)
        f = open(logpath, "a+")
        f.write(filepath + "," + image_id + "\n")
        f.close()
        print("-" * 20)

    except:
        print("!" * 40)
        print("Unexpected error:", sys.exc_info()[0])
    else:
        # counter += 1
        if args.verbose:
            # print("--- image converted ---")
            # print("time elapsed: {:.4f}".format(time.time() - start))
            print("-" * 20)

    return child

def main():
    # time the entire script
    overall_start = time.time()

    # counter = 0
    # missing_count = 0

    if args.verbose:
        print("textfile:",args.textfile)
        print("convert_path:",args.convert_path)
        print("start_line:",args.start_line)
        # print("missing:",args.missing)
        print("lowdensity:",args.lowdensity)

    filepaths = []
    image_ids = []

    # time loading filepaths
    start = time.time()

    # read in paths from textfile
    with open(args.textfile, "r") as f:
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

    print("*" * 20)
    print("checking the first filepath and id:")
    print(filepaths[args.start_line], image_ids[args.start_line])
    print("*" * 20)

    # create a log file to write any errors
    now = datetime.datetime.now()
    now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    logpath = "error_log_" + now_string + ".txt"
    # missing_logpath = convert_path + "missing_log_" + now_string + ".txt"
    print("logging errors to:",logpath)
    # print("logging missing files to:",missing_logpath)

    print("length of current filepaths:",len(filepaths))

    outputnames = []
    for image_id, filepath in zip(image_ids[args.start_line:], filepaths[args.start_line:]):
        outputnames.append([args.convert_path + str(image_id) + ".jpg"])
    print("length of outputnames:",len(outputnames))

    assert len(filepaths) == len(outputnames), "!!! unmatched filepaths and outputnames !!!"

    # create pool
    # num_cpus = cpu_count()
    # es = 'Finished conversion of {} to {}'
    # p = Pool(processes=8)
    # for infn, outfn in p.imap_unordered(convert, zip(filepaths, outputnames)):
    #     if args.verbose:
    #         print(es.format(infn, outfn))

    # manage procs version
    procs = []
    maxprocs = 8 # could be cpu_count()
    for n, f in enumerate(filepaths):
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(convert(f, outputnames[n], logpath))

    print("finished converting!")
    # print("total number of items:",counter) # doesn't work with multiprocessing
    end = time.time()
    print("total time taken:", end - overall_start)
    # print("number of missing files:",missing_count)

    # futures thread pool version
    # starter = partial(convert)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as tp:
    #     fl = [tp.submit(starter, t) for t in zip(filepaths, outputnames)]
    #     for fut in concurrent.futures.as_completed(fl):
    #         fn, rv = fut.result()
    #         if rv == 0:
    #             logging.info('finished "{}"'.format(fn))

def manageprocs(proclist):
    for pr in proclist:
        if pr.poll() is not None:
            proclist.remove(pr)
    time.sleep(0.5)

if __name__ == "__main__":
    main()
