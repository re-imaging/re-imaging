# Script to read image paths from a textfile and then convert them using ImageMagick
# threaded for performance gains

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

import concurrent.futures
from functools import partial

parser = argparse.ArgumentParser(description='Script for converting images from a textfile using convert (threaded)')

parser.add_argument('textfile', help='textfile to read from')
parser.add_argument('images_path', help='path to original images folder')
parser.add_argument('convert_path', help='path to destination folder')
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('--timeout', default=30, type=int, help='timeout for convert command (default: 30)')
# parser.add_argument('--missing', action='store_true', help='write missing output file: True/False')
parser.add_argument('--lowdensity', action='store_true', help='run convert without density action (default: False)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-r', '--reverse', action='store_true', help='process text file from end to start (default: False)')
parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify or create any files (default: False)")
parser.add_argument('-w', '--web', action='store_true', help="convert lower resolution images for web (default: False)")
parser.add_argument('-e', '--check_exists', action='store_true', help="check if file already exists in target folder (default: False)")

global args
args = parser.parse_args()

if args.web:
    prearg = shlex.split("")
    # arguments = shlex.split("-colorspace sRGB -resize 300x300^>") # NB: added ">" to not increase size
    # version with more optimizations for web
    arguments = shlex.split("-strip -resize 300x300^> -sampling-factor 4:2:0 -quality 85 -colorspace sRGB") # -interlace Plane -gaussian-blur 0.05
else:
    arguments = shlex.split("-colorspace sRGB -background white -alpha background -trim +repage -flatten -resize 512x512^>")
    if args.lowdensity:
        # prearg = shlex.split("-density 72 -colorspace CMYK")
        prearg = shlex.split("-colorspace CMYK")
    else:
        prearg = shlex.split("-density 300 -colorspace CMYK")

# handle Ctrl+C - this doesn't seem to work so well?
def signal_handler(signal, frame):
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# this function converts an image
# with excessive error handling in case the Imagemagick convert call fails
def convert(argin, logpath):
# def convert(filepath, outputname):
    # print(argin)

    filepath = argin[0]
    outputname = argin[1]
    print(filepath, "-->", outputname)

    if args.check_exists:
        if os.path.isfile(outputname[0]):
            if args.verbose:
                print(">>> already exists >>>")
            return filepath, 0

    # is there an easier way to reference this?
    global prearg
    global arguments
    # global logpath

    image_id = os.path.basename(outputname[0])

    convert_cmd = ["convert"] + prearg + [":" + filepath + "[0]"] + arguments + outputname
    extension = filepath.rsplit(".", 1)[1]
    # print(extension)
    try:
        output = ""
        error = ""
        # previously pipe'ing output and universal_newlines=True
        # child = subprocess.Popen(convert_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        child = subprocess.Popen(convert_cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,error = child.communicate(timeout=args.timeout)
        # if child.returncode != 0:
        #     raise Exception(f'exception - image {image_id}')
        #     print("returncode:",child.returncode)
        #     print("output:",output)
        #     print("error:",error)
    except TimeoutExpired:

        child.kill()
        # this added end of 20190924
        if child.pid is None:
            print("child PID is None")
            pass
        else:
            print("timeout -- killing child process")
            os.kill(child.pid, signal.SIGTERM)

        print("!" * 20, "timeout --- logging problem file")
        # print("timeout --- logging problem file")
        print("filename:",filepath)
        # print("image_id:",image_id)
        print("outputname:",outputname)

        print("output:",output)
        print("error:",error)

        f = open(logpath, "a+")
        f.write(filepath + "," + image_id + "\n")
        f.close()
        # print("-" * 20)

        return filepath, 1

    except Exception:

        # this added end of 20190924
        child.kill()
        if child.pid is None:
            pass
            print("child PID is None")
        else:
            print("Unexpected error -- killing child process")
            print(sys.exc_info()[0])
            try:
                os.kill(child.pid, signal.SIGTERM)
            except:
                print("couldn't kill for some reason")
                pass
            raise

        print("!" * 20, "Exception --- logging problem file")
        print("output:",output)
        print("error:",error)
        # print("-" * 20)

        # print("Exception --- logging problem file")
        print("filename:",filepath)
        # print("image_id:",image_id)
        print("outputname:",outputname)
        f = open(logpath, "a+")
        f.write(filepath + "," + image_id + "\n")
        f.close()
        # print("-" * 20)

        return filepath, 2

    except:
        # this added end of 20190924
        child.kill()
        if child.pid is None:
            pass
            print("child PID is None")
        else:
            print("something went wrong -- killing child process")
            print(sys.exc_info()[0])
            os.kill(child.pid, signal.SIGTERM)

        print("!" * 40, "Unexpected error:")
        print("Unexpected error:", sys.exc_info()[0])

        return filepath, 3

    else:
        # counter += 1
        if args.verbose:
            print("--- image converted ---")
            # print("time elapsed: {:.4f}".format(time.time() - start))
            # print("-" * 20)

    return filepath, 0

def main():
    # time the entire script
    overall_start = time.time()

    dryRun = args.dryrun

    # counter = 0
    # missing_count = 0

    if args.verbose:
        print("textfile:",args.textfile)
        # print("image_path:",args.images_path)
        print("convert_path:",args.convert_path)
        print("start_line:",args.start_line)
        # print("missing:",args.missing)
        print("lowdensity:",args.lowdensity)
        print("reverse:",args.reverse)
        print("number of threads:",args.num_threads)

    filepaths = []
    image_ids = []

    # time loading filepaths
    start = time.time()

    p = args.images_path if args.images_path.endswith("/") else args.images_path + "/"
    print("path for reading original images:", p)

    # read in paths from textfile
    with open(args.textfile, "r") as f:
        lines = f.readlines()
        print("total lines in file:",len(lines))
        print("first file entry:",lines[0])
    for l in lines:
        substrings = l.rsplit(",", 1)
        filepaths.append(p + substrings[0].strip())
        if args.web:
            image_ids.append(substrings[0].split(".")[0])
        else:
            image_ids.append(substrings[1].strip())

    if args.reverse:
        filepaths.reverse()
        image_ids.reverse()

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

    assert len(filepaths[args.start_line:]) == len(outputnames), "!!! unmatched filepaths and outputnames !!!"

    divisions = [x for x in range(args.start_line, len(filepaths), 5000)]
    divisions.append(len(filepaths))

    # futures thread pool version
    if dryRun:
        pass
    else:
        starter = partial(convert, logpath=logpath)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as tp:
            for i, div in enumerate(divisions[:-1]):
                if args.verbose:
                    print(f'setting up threads for divisions {div}-{divisions[i+1]}')
                fl = [tp.submit(starter, t) for t in zip(filepaths[div:divisions[i+1]], outputnames[div:divisions[i+1]])]
                for fut in concurrent.futures.as_completed(fl):
                    fn, rv = fut.result()
                    if rv == 0:
                        print('finished "{}"'.format(fn))
                    elif rv < 0:
                        print('exit code > 0 in child process')
                        # fut.kill()
                    else:
                        print("converting {} failed, return code {}".format(fn, rv))

if __name__ == "__main__":
    main()
