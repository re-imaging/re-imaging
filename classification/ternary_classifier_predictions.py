# Ternary Classifier Predictions
#
# Uses a previously trained network to classify images and then saves the resulting prediction averages.
# This is then used to generate plots, see `ternary_classifier_predictions_plot.ipynb`

import numpy as np

import os
import random
import PIL.Image
import datetime

# from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.applications.vgg16 import VGG16, preprocess_input

from keras.models import Model, load_model
from keras.layers import Dense, GlobalAveragePooling2D, AveragePooling2D, Dropout, Flatten, Conv2D, Activation
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator, img_to_array # load_img
from keras.optimizers import SGD, Adam
from keras.callbacks import ModelCheckpoint

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import pickle

# this seems to help with some GPU memory issues

import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

# load model previously saved with `ternary_classifier.ipynb`
model = load_model("checkpoints/ternary_20190911_9748x/diagram-sensor-unsure_vgg16-2000.hdf5")

# import the sqlite3 database and create a cursor
db_path = os.path.expanduser("~/data/db/arxiv_db_images.sqlite3")
db = sqlite3.connect(db_path)
c = db.cursor()

# load the data saved previously from `../sqlite-scripts/db_plots.ipynb`
image_pkl_filename = "../sqlite-scripts/images_cat_year_data.pkl"

# READ PKL
with open(image_pkl_filename, "rb") as read_file:
    image_data = pickle.load(read_file)

def load_image(path):
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x

# figure out where we were up to
starting_index = 0
for i, row in enumerate(image_data):
    if(len(row) < 4):
        print("checking for starting index")
        starting_index = i
        print("first index with length < 4:",starting_index)
        break

'''
### Run prediction

Code below queryies the SQLite DB for a particular category and year and returns all of the image IDs.
These are then used to check if the converted jpg file exists.
Those files are passed to the model which gives a prediction.
The top class prediction totals are saved in the big ```image_data``` list.
Later the percentage probability for each class is calculated.
'''

sql = ('''
    SELECT images.id
    FROM images
    LEFT JOIN metadata on images.identifier = metadata.identifier
    WHERE substr(trim(cat),1,instr(trim(cat)||' ',' ')-1) = ?
    AND strftime("%Y", metadata.created) = ?
    ''')

imagefolder = os.path.expanduser("~/all/")
classes = ["diagram", "sensor", "unsure"]
now = datetime.datetime.now()
now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logpath = "error_log_" + now_string + ".txt"

for index, cat in enumerate(image_data[starting_index:]):
    print(cat[0]) # category string
    cat_class_totals = []
    for year in cat[1]:
        print(cat[0], year) # year

        c.execute(sql, (cat[0], year))
        rows = c.fetchall()

        class_totals = [0, 0, 0]

#         print("image files:",rows)
        random.seed(4) # fixed seed for reproducable results
        random.shuffle(rows)
#         print("shuffled:", rows)

        # for each category
        # get a maximum of 1000 rows from the randomly sorted results
        for i, row in enumerate(rows[:1000]):
            print(i, row)
            imagefilepath = os.path.join(imagefolder, str(row[0]) + ".jpg")
            print(imagefilepath)
            try:
                img, x = load_image(imagefilepath)
                img.verify() # verify that it is, in fact an image
            except (IOError, SyntaxError, AttributeError) as e:
                print('>>>>> Bad file:', imagefilepath) # print out the names of corrupt files
                f = open(logpath, "a+")
                f.write(imagefilepath + "\n")
                f.close()
            except:
                print('>>>>> Bad file:', imagefilepath) # print out the names of corrupt files
                f = open(logpath, "a+")
                f.write(imagefilepath + "\n")
                f.close()
            predictions = model.predict(x)
            print(predictions[0])

            ind = np.argmax(predictions)
            class_totals[ind] +=1
            pred = classes[ind]
            print(pred)

            print("*" * 20)

        print(class_totals)
        cat_class_totals.append(class_totals)
        print("-" * 40)

    print(cat_class_totals)
    image_data[index + starting_index].append(cat_class_totals)

    # WRITE PKL
    with open("ternary_classifier_predictions.pkl", "wb") as write_file:
        pickle.dump(image_data, write_file)
    print("finished writing pickle file")
    print("-" * 40)

    '''
    Write pickle file. This is used in other code, e.g. ternary_classifier_predictions.py

    This is a list in the format of

    [['category',
        ['year-1', 'year-2', 'year-3'],
        [total-1, total-2, total-3],
        [[diagram, sensor, unsure], [diagram, sensor, unsure], [diagram, sensor, unsure]]],
    ...

    e.g.

    [['acc-phys',
      ['1994', '1995', '1996'],
      [6, 16, 97],
      [[6, 0, 0], [16, 0, 0], [97, 0, 0]]],
     ['adap-org',
      ['1993', '1994', '1995', '1996', '1997', '1998', '1999'],
      [42, 32, 91, 84, 267, 354, 437],
      [[41, 0, 1],
       [12, 0, 20],
       [84, 0, 7],
       [83, 0, 1],
       [260, 0, 7],
       [310, 4, 40],
       [351, 4, 82]]],
     ['alg-geom',
      ['1993', '1994', '1995', '1996', '1997'],
      [1, 10, 31, 94, 283],
      [[1, 0, 0], [10, 0, 0], [31, 0, 0], [92, 0, 2], [258, 0, 25]]],
    '''

print("*** DONE ***")
