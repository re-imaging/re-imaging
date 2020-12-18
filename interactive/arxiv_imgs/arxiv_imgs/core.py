import functools
import os
import sys

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
# from werkzeug.security import check_password_hash
# from werkzeug.security import generate_password_hash

from flaskr.db import get_db

from annoy import AnnoyIndex

import numpy as np
import random
import math

import time

from guppy import hpy
h = hpy()
# print(h.heap())

NUM_INDEXES = 600000
# NUM_INDEXES = 1200000
NIMAGES = 100

image_list = "/home/rte/data/paths/all_images_shuf.txt"
filepaths = []

with open(image_list, "r") as f:
    lines = f.readlines()
    print("length of image text file:",len(lines))
for l in lines[:NUM_INDEXES]:
    substring = l.split(".jpg")[0]
    filepaths.append(substring)
    # image_ids.append(substrings[1].strip())
# print("length of filepaths:", len(filepaths))

# db = get_db()
# c = db.cursor()
#
# # load images from db
# c.execute("SELECT id FROM images")
# rows = c.fetchall()
# filepaths = [str(x[0]) for x in rows]
# print("number of image paths loaded:", len(filepaths))

bp = Blueprint("core", __name__, url_prefix="/core")

@bp.route("/interface", methods=["GET", "POST"])
def get_random_images():
    """If the user has selected an image, grab annoy results.
    Otherwise grab random images from the database and display.
    """

    embedding = request.form.get("embedding")
    print("embedding:", embedding)
    author = request.form.get("author")
    print("author:",author)
    category = request.form.get("category")
    print("category:",category)
    imageformat = request.form.get("imageformat")
    print("imageformat:",imageformat)
    prediction = request.form.get("prediction")
    print("prediction:",prediction)
    image_id = request.form.get("image_id")
    print("image_id:", image_id)

    # if no selected image, just get random indexes
    # else use annoy to find indexes
    # then filter using SQLite search
    # then get metadata for each image

    if not image_id:
        print("image_id:", image_id, "- getting random indexes")
        # rand_nums = random.sample(range(NUM_INDEXES), NIMAGES)
        # images = [filepaths[i] for i in rand_nums]
        images = filepaths
        random.shuffle(images)
        # print("random images", images)

        image_id = None
        embedding = None
        result_total = None
        images_shown = None
    elif request.method == "POST":
        print("name of button: ", request.form.get("btn"))

        if request.form.get("btn") == "search-images":
            print("image id:", image_id)
            print("get annoy indexes and pull images")

            start = time.time()

            ann = AnnoyIndex(300, 'angular')

            if embedding == "VGG16":
                ann_filepath = "/home/rte/re-imaging/interactive/600k_vgg_ipca.ann"
            elif embedding == "raw":
                # ann_filepath = "/home/rte/re-imaging/interactive/1200k_raw.ann"
                ann_filepath = "/home/rte/re-imaging/interactive/600k_raw.ann"
            elif embedding == "ternary":
                ann_filepath = "/home/rte/re-imaging/interactive/600k_ternary.ann"
            # else:
                # ann_filepath = "/home/rte/re-imaging/interactive/600k_vgg_ipca.ann"

            # print(h.heap())
            ann.load(ann_filepath)
            # print(h.heap())

            print(f'loading AnnoyIndex, time taken {time.time() - start}')

            start = time.time()

            nindexes = NIMAGES
            if author or category:
                nindexes = 100000

            target_index = filepaths.index(image_id)
            indexes = ann.get_nns_by_item(target_index, nindexes) # NIMAGES
            # print(f'indexes total {len(indexes)}: {indexes}')

            images = np.array(filepaths)[np.array(indexes)]
            # print("target_images:", len(images))
            # print(images)

            print(f'getting indexes, time taken {time.time() - start}')

            result_total = None
            images_shown = NIMAGES

            # previous filter-images code

            # if request.form.get("btn") == "filter-images":

    # filter
    if author or category or imageformat or prediction:
        start = time.time()

        print("there are filter arguments, running filter")
        db = get_db()
        c = db.cursor()

        sql = """
                SELECT images.id
                FROM images
                LEFT JOIN metadata on images.identifier = metadata.identifier
                WHERE metadata.authors LIKE ?
                AND metadata.cat LIKE ?
                AND imageformat LIKE ?
                AND vggpred LIKE ?
                """
        # search_count = 0
        # if author:
        #     sql += " metadata.authors LIKE ?"
        #     search_count += 1
        # if category:
        #     if search_count > 0: sql += " AND"
        #     sql += " metadata.cat LIKE ?"
        #     search_count += 1
        # if imageformat:
        #     if search_count > 0: sql += " AND"
        #     sql += " imageformat LIKE ?"
        #     search_count += 1
        # if category:
        #     if search_count > 0: sql += " AND"
        #     sql += " vggpred LIKE ?"
        #     search_count += 1
        # print("printing sql")
        # print(sql)

        print("sql arguments:", "%"+author+"%", category+"%", imageformat+"%", prediction+"%")

        c.execute(sql, ("%"+author+"%", category+"%", imageformat+"%", prediction+"%"))
        rows = c.fetchall()
        result_total = len(rows)
        # print(rows)

        found = [row[0] for row in rows]
        print(f'querying SQLite for search terms, time taken {time.time() - start}')
        # print("found:", len(found), found)

        start = time.time()

        matches = []
        for im in images[:]: # NIMAGES
            # print("image:", type(im), im)
            # if np.any(np.array(found) == im):

            if len(matches) >= NIMAGES:
                break

            # for f in found:
            if int(im) in found:
                # print(f)
                # if int(im) == f:
                    # print(f'match! {im} in found!')
                matches.append(im)
                    # break
                # if len(images) >= NIMAGES:
                #     break
                # images.append(str(row[0])) # = [str(r) for r in row]
        print("len(matches):", len(matches))
        images = matches[:NIMAGES]
        images_shown = len(images)
        # print(images)
        print(f'filtering for matches, time taken {time.time() - start}')
        # metadata.append(items)

        # image_id = None

        # elif request.form.get("btn") == "search-features":

    start = time.time()

    images = images[:NIMAGES]

    # only run the below code if we haven't already grabbed the database stuff?
    db = get_db()
    c = db.cursor()
    metadata = []

    meta_sql = """
                SELECT images.identifier, filename, x, y, imageformat, creator,
                metadata.created, metadata.cat, metadata.authors, metadata.title,
                images.vggpred
                FROM images
                LEFT JOIN metadata ON images.identifier == metadata.identifier
                WHERE images.id IS ?
                """

    for i in images:
        # print("i:",i)
        c.execute(meta_sql, (i,))
        rows = c.fetchall()
        for row in rows:
            items = [str(r) for r in row]
            # print(items)
            metadata.append(items)
    print("metadata length:", len(metadata))
    # print(metadata)

    print(f'querying metadata, time taken {time.time() - start}')

    # images_shown = None
    # if result_total:
    #     images_shown = min(images_shown, result_total)
    print("images_shown:", images_shown)

    si_meta = None
    if image_id:
        c.execute(meta_sql, (image_id,))
        rows = c.fetchall()
        # for row in rows:
        si_meta = [str(r) for r in rows[0]]
            # si_meta = [row[0] for row in rows]
        print("si_meta:", si_meta)

    # print(h.heap())
    print(f'calling return render_template, with {len(images)} images: {images}')
    return render_template('core/opening.html', images=images, metadata=metadata,
                            enumerate=enumerate, prev_image_id=image_id, result_total=result_total,
                            images_shown=images_shown, embedding=embedding, si_meta=si_meta,
                            category=category, author=author, imageformat=imageformat,
                            prediction=prediction)

@bp.route('/test')
def get_test_image():
    """Just show one image as a test."""

    # filename = "/home/rte/data/images/web/120k/5478268.jpg"
    # images = [url_for("static", filename="/all/7732085.jpg")]
    images = ["7732085"]
    return render_template("core/opening.html", images=images)
