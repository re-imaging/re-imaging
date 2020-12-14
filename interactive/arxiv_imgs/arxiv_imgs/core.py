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
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db

from annoy import AnnoyIndex

import numpy as np
import random
import math

NUM_INDEXES = 600000
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

# db = get_db()
# c = db.cursor()
#
# # load images from db
# c.execute("SELECT id FROM images")
# rows = c.fetchall()
# filepaths = [str(x[0]) for x in rows]
# print("number of image paths loaded:", len(filepaths))

bp = Blueprint("core", __name__, url_prefix="/core")

# def eprint(*args, **kwargs):
#     print(*args, file=sys.stderr, **kwargs)

# @bp.route("/connect")
# def get_connecting_images(images):
#     print(images)
#     return render_template('core/connect.html', images=images)


# @bp.route("/<int:id>", methods=["GET", "POST"])
# def get_nn(image_id):
#     """Get images using annoy and then show to user."""
#     if request.method == "POST":
#         image_id = request.form.get("image_id")
#
#         # try:
#         print("image id:", image_id)
#         print("get annoy indexes and pull images")
#
#         ann = AnnoyIndex(300, 'angular')
#         ann.load("/home/rte/re-imaging/interactive/600k_vgg_ipca.ann")
#
#         target_index = filepaths.index(image_id + ".jpg")
#         indexes = ann.get_nns_by_item(target_index, NIMAGES)
#         print("indexes:", indexes)
#         images = np.array(filepaths)[np.array(indexes)]
#         print("target_images:",images)

# @bp.route("/filter", methods=["GET", "POST"])
# def get_filtered_images():
#
#     return render_template('core/opening.html', images=images, metadata=metadata,
#                             enumerate=enumerate, prev_image_id=image_id)

@bp.route("/interface", methods=["GET", "POST"])
def get_random_images():
    """If the user has selected an image, grab annoy results.
    Otherwise grab random images from the database and display.
    """

    embedding = request.form.get("embedding")

    if request.method == "POST":
        print("name of button: ", request.form.get("btn"))

        if request.form.get("btn") == "filter-images":
            db = get_db()
            c = db.cursor()

            images = []

            author = request.form.get("author")
            print("author:",author)
            category = request.form.get("category")
            print("category:",category)

            sql = """
                    SELECT images.id
                    FROM images
                    LEFT JOIN metadata on images.identifier = metadata.identifier
                    WHERE metadata.authors LIKE ?
                    AND metadata.cat LIKE ?
                    """
            # if author or category:
            #     sql = sql + "WHERE"

            c.execute(sql, ("%"+author+"%", category+"%"))
            rows = c.fetchall()
            result_total = len(rows)

            for row in rows[:NIMAGES]:
                images.append(str(row[0])) # = [str(r) for r in row]
            print(images)
            # metadata.append(items)

            image_id = None

        elif request.form.get("btn") == "search-images":
            image_id = request.form.get("image_id")

            # try:
            print("image id:", image_id)
            print("get annoy indexes and pull images")

            ann = AnnoyIndex(300, 'angular')

            # embedding = request.form.get("embedding")
            print("embedding:", embedding)

            if embedding == "VGG16":
                ann_filepath = "/home/rte/re-imaging/interactive/600k_vgg_ipca.ann"
            elif embedding == "raw":
                ann_filepath = "/home/rte/re-imaging/interactive/600k_raw.ann"
            elif embedding == "ternary":
                ann_filepath = "/home/rte/re-imaging/interactive/600k_ternary.ann"
            else:
                ann_filepath = "/home/rte/re-imaging/interactive/600k_vgg_ipca.ann"

            ann.load(ann_filepath)

            target_index = filepaths.index(image_id)
            indexes = ann.get_nns_by_item(target_index, NIMAGES)
            print("indexes:", indexes)
            images = np.array(filepaths)[np.array(indexes)]
            print("target_images:",images)

            result_total = None

            # return render_template('core/opening.html', images=images)
            # return render_template('core/opening.html', images=target_images)
            # return redirect(url_for("core.get_random_images", images=images))
            # return redirect(url_for("core.get_connecting_images", images=target_images))
            # print("does it get to here?")
            # except:
            #     # return error
            #     print("error getting results")

            # db = get_db()
            # c = db.cursor()
            # metadata = []
            # for i in images:
            #     print("i:",i)
            #     c.execute("SELECT identifier, filename, x, y, imageformat, creator FROM images WHERE id IS ?", i)
            #     rows = c.fetchall()
            #     metadata.append(rows)
            # print(metadata)
            #
            # print("calling return render_template, with images:", images)
            # return render_template('core/opening.html', images=images, metadata=metadata, enumerate=enumerate)

        # elif request.form.get("btn") == "search-features":

    else:
        # db = get_db()
        # c = db.cursor()
        #
        # load images from db
        # c.execute("SELECT id FROM metadata ORDER BY RANDOM() LIMIT 60")
        # rows = c.fetchall()
        # images = [str(x[0]) + ".jpg" for x in rows]
        # print("number of rows:",len(rows))

        # load images from text file
        rand_nums = random.sample(range(NUM_INDEXES), NIMAGES)
        images = [filepaths[i] for i in rand_nums]
        print("random images", images)

        image_id = None

        result_total = None

    # only run the below code if we haven't already grabbed the database stuff?
    # if not metadata:
    db = get_db()
    c = db.cursor()
    metadata = []

    for i in images:
        # print("i:",i)
        c.execute("SELECT identifier, filename, x, y, imageformat, creator FROM images WHERE id IS ?", (i,))
        rows = c.fetchall()
        for row in rows:
            items = [str(r) for r in row]
            # print(items)
            metadata.append(items)
    print(metadata)

    # print("calling return render_template, with images:", images)
    # return render_template('core/opening.html', images=images, metadata=metadata, enumerate=enumerate)
    images_shown = None
    if result_total:
        images_shown = min(NIMAGES, result_total)
    print("images_shown:", images_shown)

    print("calling return render_template, with images:", images)
    return render_template('core/opening.html', images=images, metadata=metadata,
                            enumerate=enumerate, prev_image_id=image_id, result_total=result_total,
                            images_shown=images_shown, embedding=embedding)

@bp.route('/test')
def get_test_image():
    """Just show one image as a test."""

    # filename = "/home/rte/data/images/web/120k/5478268.jpg"
    # images = [url_for("static", filename="/all/7732085.jpg")]
    images = ["7732085"]
    return render_template("core/opening.html", images=images)
