#!/usr/bin/env python
# coding: utf-8

# In[74]:


import os
import random


# In[75]:


from PIL import Image
# from pillow import Image


# In[76]:


import numpy as np
import matplotlib.pyplot as plt


# In[77]:


import pickle


# In[78]:


import time


# In[79]:


import keras
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions, preprocess_input
from keras.models import Model


# In[80]:


model = keras.applications.VGG16(weights='imagenet', include_top=True)


# In[81]:


print("model loaded")
model.summary()


# In[82]:


def load_image(path):
    img = image.load_img(path, target_size=model.input_shape[1:3])
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return img, x


# In[83]:


# set up the feature extractor

feat_extractor = Model(inputs=model.input, outputs=model.get_layer("fc2").output)
print("feature extractor setup")
feat_extractor.summary()


# In[84]:


# create a list of all the category/year folders

paths = []

parent_dir = '/home/rte/data/images/cat/'
category = ''
year = ''

categories = [f.path for f in os.scandir(parent_dir) if f.is_dir()]
# print(categories)

for c in categories:
    path = [f.path for f in os.scandir(c) if f.is_dir()]
#     print(path)
    paths.append(path)

# print(paths)
for p in paths:
    p.sort()
print("----- paths -----")
print(paths)


# In[ ]:


# big loop here

for cat in paths[4:]:
    for d in cat:
        current_path = d
        print("current path: " + current_path)
        category = current_path.split('/')[6]
        year = current_path.split('/')[7]
        print("category: " + category)
        print("year: " + str(year))
        
        image_extensions = ['.jpg', '.png', '.jpeg']   # case-insensitive (upper/lower doesn't matter)

        images = [os.path.join(dp, f) for dp, dn, filenames in os.walk(current_path) for f in filenames if os.path.splitext(f)[1].lower() in image_extensions]
        num_x = len(images)
        print("keeping %d images to analyze" % num_x)
        
        
        
        tic = time.clock()

        features = []
        for i, image_path in enumerate(images):
            if i % 500 == 0:
                toc = time.clock()
                elap = toc-tic;
                print("analyzing image %d / %d. Time: %4.4f seconds." % (i, len(images),elap))
                tic = time.clock()
            img, x = load_image(image_path)
            
            
            feat = feat_extractor.predict(x)[0]
            features.append(feat)

        print('finished extracting features for %d images' % len(images))

        # write images, features to a pickle file

        f = "features_" + category + "_" + year + "_vgg_x" + str(num_x) + ".pickle"

        print(f)

        # WRITE
        with open(f, "wb") as write_file:
            pickle.dump([images, features], write_file)
            write_file.close()


# In[ ]:




