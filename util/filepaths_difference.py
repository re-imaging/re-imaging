import argparse
import itertools
import os
import time
import sys
import datetime

parser = argparse.ArgumentParser(description='Script for generating text file from filepaths and folder')

parser.add_argument('textfile', help='textfile to read from')
parser.add_argument('target_folder', help='path to destination folder')
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('-m', '--missing', action='store_true', help='write missing output file')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

# compares a list of filepaths with the folders in target_folder
# generates a resulting textfile if --missing is used
# text file written to script folder with date in filename
def compare_list_with_folder(textfile, target_folder, start_line, missing):
    counter = 0
    missing_count = 0

    if args.verbose:
        print("textfile:",textfile)
        print("target_folder:",target_folder)
        print("start_line:",start_line)
        print("missing:",args.missing)

    filepaths = []
    image_ids = []

    # loading filepaths timer
    start = time.time()
    # whole script timer
    overall_start = time.time()

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

    print("*" * 20)
    print("checking the first filepath and id:")
    print(filepaths[start_line], image_ids[start_line])
    print("*" * 20)

    # create a log file to write any errors or missing files
    now = datetime.datetime.now()
    now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    # logpath = target_folder + "error_log_" + now_string + ".txt"
    missing_logpath = "missing_log_" + now_string + ".txt"
    # print("logging errors to:",logpath)
    print("logging missing files to:",missing_logpath)

    # iterate over all of the filepaths and check what is already in folder
    for image_id, filepath in zip(image_ids[start_line:], filepaths[start_line:]):
        start = time.time()

        outputname = [target_folder + str(image_id) + ".jpg"]
        if args.verbose:
            print("filename:",filepath)
            print("image_id:",image_id)
            print("outputname:",outputname)

        # test if image is already in the folder
        if os.path.isfile(str(outputname[0])):
            if args.verbose:
                print("file already exists!:",outputname)

        else:
            missing_count += 1

            if args.verbose:
                print("*" * 20)
                print("file doesn't exist")

            # write file path to missing log
            if args.missing:
                f = open(missing_logpath, "a+")
                f.write(filepath + "," + image_id + "\n")
                f.close()

    print("length of original filepaths:",len(filepaths))
    print("length of current filepaths:",len(filepaths))

    print("finished checking folder")

    end = time.time()
    print("total time taken:", end - overall_start)
    print("number of missing files:",missing_count)

def main():
    global args
    args = parser.parse_args()

    compare_list_with_folder(args.textfile, args.target_folder, args.start_line, args.missing)

if __name__ == "__main__":
    main()
