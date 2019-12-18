from PIL import Image
import argparse
import datetime

# used for converting images that couldn't be converted using ImageMagick convert
# NB: recommended to use parallel_convert_futures.py first, then run this on images that couldn't be converted

parser = argparse.ArgumentParser(description='Script for converting images from a textfile')

parser.add_argument('textfile', help='textfile to read from')
parser.add_argument('convert_path', help='path to destination folder')
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

# script to convert a list of image paths via Python PIL (pillow)

global args
args = parser.parse_args()

def convert(filepath, outputname, logpath):

    try:
        im = Image.open(filepath)
        rgb_im = im.convert('RGB')
        rgb_im.save(outputname[0])
    except:
        print("some kind of exception")
        with open(logpath, "a+") as f:
            f.write(filepath + "\n")

def main():

    filepaths = []
    image_ids = []

    with open(args.textfile, "r") as f:
        lines = f.readlines()
        print("total lines in file:",len(lines))
        print("first file entry:",lines[0])
    for l in lines:
        substrings = l.rsplit(",", 1)
        filepaths.append(substrings[0].strip())
        image_ids.append(substrings[1].strip())

    print("total filepaths:",len(filepaths))
    print("total image_ids:",len(image_ids))

    now = datetime.datetime.now()
    now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    logpath = "error_log_" + now_string + ".txt"
    print("logging errors to:",logpath)

    print("length of current filepaths:",len(filepaths))

    outputnames = []
    for image_id, filepath in zip(image_ids[args.start_line:], filepaths[args.start_line:]):
        outputnames.append([args.convert_path + str(image_id) + ".jpg"])
    print("length of outputnames:",len(outputnames))

    assert len(filepaths[args.start_line:]) == len(outputnames), "!!! unmatched filepaths and outputnames !!!"

    for fn, on in zip(filepaths, outputnames):
        if(args.verbose):
            print("attempting to convert:",fn,on)
        convert(fn, on, logpath)

if __name__ == "__main__":
    main()
