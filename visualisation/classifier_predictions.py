import os
import random

import argparse

from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

import pickle
import json
import gzip
import bz2

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

parser = argparse.ArgumentParser(description='Script for getting image features using VGG16 network and saving pickle')

# parser.add_argument('paths_file', help='textfile to read image paths from')
parser.add_argument('textfile', help="path to textfile of paths")
parser.add_argument('images_path', help="path to folder of images")
# parser.add_argument('savedir', help="path to folder to save pickles")
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
parser.add_argument('--end_line', default=0, type=int, help='line to read textfile to (default: 0)')
parser.add_argument('-s', '--slice_size', default=50000, type=int, help='size of each slice to process (default: 50000)')
# parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-t', '--timing', action='store_true', help='timing output')
parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify or create any files (default: False)")

global args
args = parser.parse_args()

model = keras.applications.VGG16(weights='imagenet', include_top=True)
print("model loaded")
model.summary()

# model = keras.applications.VGG16(weights='imagenet', include_top=True)

# print("model loaded")
# model.summary()

def load_image(path):
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x

# set up the feature extractor

# feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)
# print("feature extractor setup")
# feat_extractor.summary()

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
end_line = args.end_line if args.end_line > 0 else len(filepaths)
slices = [i for i in range(args.start_line + increment,
                            end_line,
                            increment)]
slices.append(end_line) # add the total length at the end
print("slices:",slices)
slice_start = args.start_line

if args.dryrun is False:
    for slice_end in slices:
        writefile = "predictions_1m.txt"
        f = open(writefile, "a+")

        tic = time.clock()

        paths_slice = filepaths[slice_start:slice_end]

        # predictions = []

        for i, image_path in enumerate(paths_slice):
            if i % 500 == 0:
                toc = time.clock()
                elap = toc-tic;
                print("analyzing image %d / %d. Time: %4.4f seconds." % (i, len(paths_slice),elap))
                tic = time.clock()
            img, x = load_image(args.images_path + image_path)

            # make prediction
            prediction = model.predict(x)
            # features.append(feat)
            # print(image_path, feat)

            # write data to file

            f.write(os.path.basename(image_path).split(".")[0])
            for _, pred, prob in decode_predictions(prediction)[0]:
                # print("predicted %s with probability %0.3f" % (pred, prob))
                f.write("," + str(pred) + "," + str(prob))
            f.write("\n")

        print('finished extracting features for %d images' % len(paths_slice))

        f.close()

        # write images, features to a pickle file

        # savefilename = args.savedir + "features_" + str(slice_start) + "_" + str(slice_end) + "_vgg.pkl.pbz2"

        slice_start = slice_end

        # print(f)

        # WRITE COMPRESSED JSON
        # with gzip.GzipFile(savefilename, 'w') as fout:
        #     fout.write(json.dumps(features).encode('utf-8'))
        #
        # print("finished saving compressed json")

        # WRITE COMPRESSED pickle
        # with bz2.BZ2File(savefilename, 'w') as write_file:
        #     pickle.dump(features, write_file)

        # WRITE PICKLE
        # with open(savefilename, "wb") as write_file:
        #     pickle.dump([paths_slice, features], write_file)
        #     write_file.close()
        #     print("writing pickle")
