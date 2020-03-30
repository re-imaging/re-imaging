# # Ternary Classifier
#
# Create a classifier model using the VGG16 architecture and train it to classify between three classes. Originally used with the arXiv images dataset and the classes of diagram, sensor, and unsure.
#
# Draws upon code from Florian Offert: https://github.com/zentralwerkstatt/explain.ipynb/blob/master/train.ipynb

import warnings
warnings.filterwarnings('ignore')

import numpy as np

import os
import sys
import glob
import random
from IPython.display import clear_output, display
import PIL.Image

# from keras.applications.inception_v3 import InceptionV3, preprocess_input
# from keras.applications.vgg16 import VGG16, preprocess_input
# from keras.applications.densenet import DenseNet121 as DenseNet, preprocess_input
from keras.applications.inception_resnet_v2 import InceptionResNetV2 as ResNet, preprocess_input

from keras.models import Model, load_model
from keras.layers import Dense, GlobalAveragePooling2D, AveragePooling2D, Dropout, Flatten, Conv2D, Activation
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator, img_to_array # load_img
from keras.optimizers import SGD, Adam
from keras.callbacks import ModelCheckpoint

import matplotlib.pyplot as plt

# floating point 16

import keras.backend as K

# dtype='float16'
dtype='float32'
K.set_floatx(dtype)

# default is 1e-7 which is too small for float16.  Without adjusting the epsilon, we will get NaN predictions because of divide by zero problems
K.set_epsilon(1e-4)


# this seems to help with some GPU memory issues

import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)


# In[13]:


# train_dir = '/home/rte/data/images/random/seq/classes/train/'
# val_dir = '/home/rte/data/images/random/seq/classes/val'

train_dir = '/home/rte/data/images/classification/labelled/train/'
val_dir = '/home/rte/data/images/classification/labelled/val'

classes = 3
batch_size = 32
epochs = 2000
save_iter = 50
# save_iter = 25
finetune = False
weights = 'imagenet'
size = 224 # VGG16
# size = 299 # V3
freeze = 164 # V3, up to and including mixed5
freeze = 20 # VGG16, up to and including
# cpath = 'diagram-sensor-unsure_vgg16-{epoch:02d}.hdf5'
cpath = 'diagram-sensor-unsure_dnet-{epoch:02d}.hdf5'
checkpoints_path = "checkpoints/"
init_epoch = 1525


# In[14]:


def add_new_last_layer_v3(base_model, classes):
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(classes, activation='softmax', name='Predictions')(x)
    model = Model(input=base_model.input, output=predictions)
    return model

def setup_to_finetune(model):
    for layer in model.layers[:freeze]:
        layer.trainable = False
    for layer in model.layers[freeze:]:
        layer.trainable = True
    model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])

def setup_to_train(model):
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])


train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(size, size),
    batch_size=batch_size,
)

validation_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(size, size),
    batch_size=batch_size,
)


# In[16]:


nb_train_samples = 7799
nb_validation_samples = 1949


# Train using stochastic gradient descent. Results were mixed using Adam.

# In[17]:


# We need to define the input shape, see
# https://stackoverflow.com/questions/49043955/shape-of-input-to-flatten-is-not-fully-defined-got-none-none-64
# base_model = VGG16(weights=None, input_shape=(size, size, 3), include_top=False)
# base_model = InceptionV3(weights=weights, input_shape=(size, size, 3), include_top=False)
# base_model = DenseNet(weights=None, input_shape=(size,size,3), include_top=False)
base_model = ResNet(weights=None, input_shape=(size,size,3), include_top=False)
base_model.summary()

# freeze layers
# for layer in base_model.layers:
#     layer.trainable = False

layer_dict = dict([(layer.name, n) for n, layer in enumerate(base_model.layers)])
model = add_new_last_layer_v3(base_model, classes)
# model.summary()

# if finetune: setup_to_finetune(model)
# else: setup_to_train(model)

model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])
# model.compile(optimizer="adam", loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()


# In[18]:


class_weights = {0: 1,
                1: 18,
                2: 14}


# In[ ]:


# callbacks = [
#     EpochCheckpoint(checkpoints_path, every=25, startAt=),
#     CSVLogger("log.csv", separator=',', append=False)
# ]


# In[20]:


history = model.fit_generator(
    train_generator,
    epochs=epochs,
    validation_data=validation_generator,
    class_weight=class_weights,
    steps_per_epoch=nb_train_samples // batch_size,
    validation_steps=nb_validation_samples // batch_size,
    initial_epoch=init_epoch,
    callbacks=[ModelCheckpoint(cpath, period=save_iter)])

# keras.callbacks.ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=False, save_weights_only=False, mode='auto', period=1)


# In[ ]:


# plot training metrics

# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
