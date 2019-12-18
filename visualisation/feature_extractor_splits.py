import os
import random

import argparse

from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

import pickle

import time

import keras
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions, preprocess_input
from keras.models import Model

import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
config.log_device_placement = True  # to log device placement (on which device the operation ran)
sess = tf.Session(config=config)
set_session(sess)  # set this TensorFlow session as the default session for Keras

parser = argparse.ArgumentParser(description='Script for getting image metadata and writing to database')

# parser.add_argument('paths_file', help='textfile to read image paths from')
parser.add_argument('textfile', help="path to textfile of paths")
parser.add_argument('images_path', help="path to folder of images")
parser.add_argument('savedir', help="path to folder to save pickles")
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('-s', '--slice_size', default=10000, type=int, help='size of each slice to process (default: 2500)')
# parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-t', '--timing', action='store_true', help='timing output')
# parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify or create any files (default: False)")

global args
args = parser.parse_args()

model = keras.applications.VGG16(weights='imagenet', include_top=True)

print("model loaded")
model.summary()

def load_image(path):
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x

# set up the feature extractor

feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)
print("feature extractor setup")
feat_extractor.summary()

# create a list of all the category/year folders

filepaths = []

with open(args.textfile, "r", encoding="ISO-8859-1") as f:
    lines = f.readlines()
    print(len(lines))
    print(lines[0])
for l in lines:
    # substrings = l.rsplit(",", 1)
    filepaths.append(l.strip())
    # image_ids.append(substrings[1].strip())

print("filepaths test:")
print(filepaths[:20])

# break work up into chunks so as to limit memory usage
increment = args.slice_size
slices = [i for i in range(args.start_line + increment, len(filepaths), increment)]
slices.append(len(filepaths)) # add the total length at the end
print("slices:",slices)
slice_start = args.start_line

for slice_end in slices:
    # current_path = d
    # print("current path: " + current_path)
    # category = current_path.split('/')[6]
    # year = current_path.split('/')[7]
    # print("category: " + category)
    # print("year: " + str(year))

    # image_extensions = ['.jpg', '.png', '.jpeg']   # case-insensitive (upper/lower doesn't matter)

    # images = [os.path.join(dp, f) for dp, dn, filenames in os.walk(current_path) for f in filenames if os.path.splitext(f)[1].lower() in image_extensions]
    # num_x = len(images)
    # print("keeping %d images to analyze" % num_x)

    tic = time.clock()

    paths_slice = filepaths[slice_start:slice_end]

    features = []
    for i, image_path in enumerate(paths_slice):
        if i % 500 == 0:
            toc = time.clock()
            elap = toc-tic;
            print("analyzing image %d / %d. Time: %4.4f seconds." % (i, len(paths_slice),elap))
            tic = time.clock()
        img, x = load_image(args.images_path + image_path)

        feat = feat_extractor.predict(x)[0]
        features.append(feat)

    print('finished extracting features for %d images' % len(paths_slice))

    slice_start = slice_end


    # write images, features to a pickle file

    savefilename = args.savedir + "features_" + str(slice_start) + "_" + str(slice_end) + "_vgg.pkl"

    print(f)

    # WRITE
    with open(savefilename, "wb") as write_file:
        pickle.dump([paths_slice, features], write_file)
        write_file.close()
        print("writing pickle")
