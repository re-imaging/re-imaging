#!/usr/bin/env python
# coding: utf-8

# In[38]:


import os
import random
import pickle
import time
import datetime


# In[26]:


from PIL import Image
# from pillow import Image


# In[27]:


from matplotlib.pyplot import imshow


# In[28]:


import numpy as np
import matplotlib.pyplot as plt


# In[29]:


from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


# In[30]:


from matplotlib.pyplot import imshow


# In[31]:


perp = 50
bPCA = True
num_iterations = 2000


# In[33]:


pickle_folder = '/home/rte/re-imaging/visualisation/'

paths = []

for file in os.listdir(pickle_folder):
    if file.endswith(".pickle"):
        paths.append(os.path.join(pickle_folder, file))
paths.sort()
# print(paths)

for p in paths:
    print(p)


# In[ ]:


# loop here

for p in paths[:]:
    print(p)
    
    category = p.split('_')[1]
    year = p.split('_')[2]
    print("category: " + category)
    print("year: " + str(year))

    with open(p, "rb") as read_file:
        images, features = pickle.load(read_file)
        read_file.close()
    
    # check that we still have the features and list of images
    print("----- checking images and features -----")
    print("length of images: " + str(len(images)))
    print("length of features: " + str(len(features)))
    for img, f in list(zip(images, features))[0:5]:
        print("image: %s, features: %0.2f,%0.2f,%0.2f,%0.2f... "%(img, f[0], f[1], f[2], f[3]))
    
    if len(images) >= 300:
        features = np.array(features)
        print("----- running pca across features -----")
        pca = PCA(n_components=300)
        pca.fit(features)

        pca_features = pca.transform(features)

        X = np.array(pca_features)
        X.shape
        tsne = TSNE(n_components=2, learning_rate=150, perplexity=perp, angle=0.2, verbose=2, n_iter=num_iterations).fit_transform(X)

        # write pickle
        print("writing tsne pickle")

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

        filename = "tSNE_" + category + "_" + year + "_n" + str(num_iterations) + "_p" + str(perp) + "_" + st
        print(filename + ".pickle")
        
        with open(filename + ".pickle", "wb") as write_file:
            pickle.dump([images, tsne], write_file)
            write_file.close()
            
        # normalise points
        tx, ty = tsne[:,0], tsne[:,1]
        tx = (tx-np.min(tx)) / (np.max(tx) - np.min(tx))
        ty = (ty-np.min(ty)) / (np.max(ty) - np.min(ty))

        width = 4000
        height = 3000
        max_dim = 100

        full_image = Image.new('RGBA', (width, height))
        for img, x, y in zip(images, tx, ty):
            tile = Image.open(img)
            if tile.width > 100 and tile.height > 100:
                rs = max(1, tile.width/max_dim, tile.height/max_dim)
                tile = tile.resize((int(tile.width/rs), int(tile.height/rs)), Image.ANTIALIAS)
                full_image.paste(tile, (int((width-max_dim)*x), int((height-max_dim)*y)), mask=tile.convert('RGBA'))
            else:
                print("tile has width or height of zero!")
        plt.figure(figsize = (16,12))
        imshow(full_image)

        print(filename)
        full_image.save(filename + ".png")
    else:
        print("selected dataset has less than 300 items")

