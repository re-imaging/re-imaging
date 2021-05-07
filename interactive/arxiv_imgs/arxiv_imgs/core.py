import functools
import os
import sys
import copy

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

image_list = "/home/rte/data/paths/600k_from_all_images_shuf.txt"
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
def get_images():
    """If the user has selected an image, grab annoy results.
    Otherwise grab random images from the database and display.
    """

    # if request.form.get('category'):
    #     print("redirect here")
    #     return redirect(request.path)

    def set_param(form, argument):
        print(f'form: {form}')
        print(f'argument: {argument}')
        value = ''
        if form:
            value = form
        elif argument:
            value = argument
        return value

    # search_select = request.form.get("search_select")
    search_select = set_param(request.form.get("search_select"), request.args.get('search-mode'))
    print(f'search_select: {search_select}')
    embedding = request.form.get("embedding")
    print("embedding:", embedding)
    image_id = request.form.get("image_id")
    print("image_id:", image_id)

    # filters
    category = set_param(request.form.get("category"), request.args.get('category'))
    print("category:",category)
    category_name = set_param(request.form.get("category-name"), request.args.get('category_name'))
    print("category_name:",category_name)
    imageformat = request.form.get("imageformat")
    print("imageformat:",imageformat)
    prediction = request.form.get("prediction")
    print("prediction:",prediction)
    author = request.form.get("author")
    print("author:",author)
    title = request.form.get("title")
    print("title:",title)
    creator = request.form.get("creator")
    print("creator:",creator)
    caption = request.form.get("caption")
    print("caption:",caption)
    date_start = request.form.get("date-start")
    print("date_start:",date_start)
    date_end = request.form.get("date-end")
    print("date_end:",date_end)
    # abstract = request.form.get("abstract")
    # print("abstract:",abstract)
    # identifier = request.form.get("identifier")
    # print("identifier:",identifier)

    # filter_arguments = {
    #     "metadata.cat": category+"%" if category else None,
    #     "imageformat": imageformat+"%" if imageformat else None,
    #     "prediction": prediction+"%" if prediction else None,
    #     "metadata.authors": "%"+author+"%" if author else None,
    #     "creator": creator+"%" if creator else None,
    #     "title": "%"+title+"%" if title else None
    # }

    filter_arguments = {}
    # if category: filter_arguments["metadata.cat"] = category+"%"
    # if imageformat: filter_arguments["imageformat"] = imageformat+"%"
    # if prediction: filter_arguments["vggpred"] = prediction+"%"
    # if author: filter_arguments["metadata.authors"] = "%"+author+"%"
    # if title: filter_arguments["title"] = "%"+title+"%"
    # if creator: filter_arguments["creator"] = creator+"%"
    if category_name:
        filter_arguments["metadata.cat"] = f'LIKE "{category_name}%"'
    elif category:
        filter_arguments["metadata.cat"] = f'LIKE "{category}%"'
    if imageformat: filter_arguments["imageformat"] = f'LIKE "{imageformat}%"'
    if prediction: filter_arguments["vggpred"] = f'LIKE "{prediction}%"'
    if author: filter_arguments["metadata.authors"] = f'LIKE "%{author}%"'
    if title: filter_arguments["title"] = f'LIKE "%{title}%"'
    if creator: filter_arguments["creator"] = f'LIKE "{creator}%"'
    if caption: filter_arguments["captions.caption"] = f'LIKE "%{caption}%"'
    if date_start: filter_arguments["metadata.created"] = f'BETWEEN "{date_start}" AND "{date_end}"'
    # if abstract: filter_arguments["metadata.abstract"] = f'LIKE "%{abstract}%"'
    # if identifier: filter_arguments["metadata.identifier"] = f'LIKE "{identifier}%"'
    # print("sql arguments:", "%"+author+"%", category+"%", imageformat+"%", prediction+"%")


    # if no selected image, just get random indexes
    # else use annoy to find indexes
    # then filter using SQLite search
    # then get metadata for each image

    if search_select == None or search_select == "": # not image_id and
        print("image_id:", image_id, "- getting random indexes")
        # rand_nums = random.sample(range(NUM_INDEXES), NIMAGES)
        # images = [filepaths[i] for i in rand_nums]
        images = copy.deepcopy(filepaths) # only shuffle the copy
        random.shuffle(images)
        # print("random images", images)

        image_id = None
        embedding = None
        result_total = None
        images_shown = NIMAGES
    else: # request.method == "POST":
        print("--- POST")
        print("name of button: ", request.form.get("btn"))

        if search_select != None: # request.form.get("btn") == "Search images":
            if embedding == "random": # or image_id == ""
                print("image_id:", image_id, "- getting random indexes")
                # rand_nums = random.sample(range(NUM_INDEXES), NIMAGES)
                # images = [filepaths[i] for i in rand_nums]
                images = copy.deepcopy(filepaths)
                random.shuffle(images)
                # print("random images", images)

                image_id = None
                embedding = None
                result_total = None
                images_shown = NIMAGES
            else:
                print("image id:", image_id)
                print(f'get annoy indexes for {embedding} and pull images')

                start = time.time()

                ann = AnnoyIndex(300, 'angular')

                if embedding == "VGG16":
                    ann_filepath = "/home/rte/re-imaging/interactive/600k_vgg_ipca.ann"
                elif embedding == "raw":
                    ann_filepath = "/home/rte/re-imaging/interactive/600k_raw.ann"
                elif embedding == "ternary":
                    ann_filepath = "/home/rte/re-imaging/interactive/600k_ternary.ann"
                elif embedding == "cats":
                    ann_filepath = "/home/rte/re-imaging/interactive/600k_cats.ann"

                # print(h.heap())
                ann.load(ann_filepath)
                # print(h.heap())

                print(f'loading AnnoyIndex, time taken {time.time() - start}')

                start = time.time()

                nindexes = NIMAGES
                # if author or category or imageformat or prediction:
                if len(filter_arguments) > 0:
                    nindexes = NUM_INDEXES

                target_index = filepaths.index(image_id)
                print(f'getting indexes for image id: {image_id} + target_index: {target_index}')
                indexes = ann.get_nns_by_item(target_index, nindexes) # NIMAGES
                # print(f'indexes total {len(indexes)}: {indexes}')

                images = np.array(filepaths)[np.array(indexes)]
                # print("target_images:", len(images))
                # print(images)

                print(f'getting indexes, time taken {time.time() - start}')

                result_total = None
                images_shown = NIMAGES

    sql_filter = """
                SELECT images.id
                FROM images
                LEFT JOIN metadata ON images.identifier == metadata.identifier
                LEFT JOIN captions ON images.caption == captions.id
                """
            # LEFT JOIN captions ON captions.image_ids LIKE '%' || metadata.identifier || '%'

    filter_count = 0
    for c, v in filter_arguments.items():
        # this is very hacky and a better way would be nice
        # handle the different ways that filters are saved
        if v is not None and v != "" and v != "%" and v != "%%":
            if filter_count == 0:
                sql_filter += f'WHERE {c} {v}'
                # sql_filter += f' {c}'
            else:
                sql_filter += f' AND {c} {v}'
                # sql_filter += f' {c}'
            filter_count += 1
    print(f'filter_count: {filter_count}')
    print(f'sql_filter query: {sql_filter}')

    if filter_count != 0:
        start = time.time()

        print("--- there are filter arguments, running filter")
        db = get_db()
        c = db.cursor()

        # format the SQL string

        # sql = """
        #         SELECT images.id
        #         FROM images
        #         LEFT JOIN metadata on images.identifier = metadata.identifier
        #         WHERE metadata.authors LIKE ?
        #         AND metadata.cat LIKE ?
        #         AND imageformat LIKE ?
        #         AND vggpred LIKE ?
        #         """
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

        # print("sql arguments:", "%"+author+"%", category+"%", imageformat+"%", prediction+"%")
        fargs = tuple((str(v) for c, v in filter_arguments.items()))
        for f in fargs:
            print("filter_arg: " + f)

        # c.execute(sql, ("%"+author+"%", category+"%", imageformat+"%", prediction+"%"))
        # c.execute(sql_filter, fargs)
        c.execute(sql_filter, )

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
    metadict = {}

    meta_sql = """
                SELECT images.identifier, filename, x, y, imageformat, creator,
                metadata.created, metadata.cat, metadata.authors, metadata.title,
                images.vggpred, captions.caption, images.id
                FROM images
                LEFT JOIN metadata ON images.identifier == metadata.identifier
                LEFT JOIN captions ON images.caption == captions.id
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

            md = {}
            md["identifier"] = str(rows[0][0])
            md["filename"] = str(rows[0][1])
            md["x"] = str(rows[0][2])
            md["y"] = str(rows[0][3])
            md["imageformat"] = str(rows[0][4])
            md["creator"] = str(rows[0][5])
            md["created"] = str(rows[0][6])
            md["cat"] = str(rows[0][7])
            md["authors"] = str(rows[0][8])
            md["title"] = str(rows[0][9]).replace('\n', ' ')
            md["vggpred"] = str(rows[0][10]).replace(",", ", ")
            md["caption"] = str(rows[0][11]).replace('\n', ' ')
            meta_image_id = str(rows[0][12])
            metadict[meta_image_id] = md
    print("metadata length:", len(metadata))
    print("metadict length:", len(metadict))
    # print(metadata)

    print(f'querying metadata, time taken {time.time() - start}')

    # images_shown = None
    # if result_total:
    #     images_shown = min(images_shown, result_total)
    print("images_shown:", images_shown)

    si_meta = None
    si_meta_d = {}

    if image_id:
        c.execute(meta_sql, (image_id,))
        rows = c.fetchall()
        # for row in rows:
        si_meta = [str(r) for r in rows[0]]
            # si_meta = [row[0] for row in rows]

        print("si_meta:", si_meta)
        md = {}
        md["identifier"] = str(rows[0][0])
        md["filename"] = str(rows[0][1])
        md["x"] = str(rows[0][2])
        md["y"] = str(rows[0][3])
        md["imageformat"] = str(rows[0][4])
        md["creator"] = str(rows[0][5])
        md["created"] = str(rows[0][6])
        md["cat"] = str(rows[0][7])
        md["authors"] = str(rows[0][8])
        md["title"] = str(rows[0][9]).replace('\n', ' ')
        md["vggpred"] = str(rows[0][10]).replace(",", ", ")
        md["caption"] = str(rows[0][11]).replace('\n', ' ')
        meta_image_id = str(rows[0][12])
        si_meta_d[image_id] = md

    bFilters = False
    if len(filter_arguments) > 0:
        bFilters = True

    # print(h.heap())
    print(f'calling return render_template, with {len(images)} images: {images}')
    return render_template('core/interface.html.j2', images=images, metadata=metadata, metadict=metadict,
                            enumerate=enumerate, prev_image_id=image_id, result_total=result_total,
                            images_shown=images_shown, embedding=embedding, search_select=search_select,
                            si_meta=si_meta, si_meta_d=si_meta_d,
                            category=category, category_name=category_name, imageformat=imageformat, prediction=prediction, author=author,
                            title=title, creator=creator, caption=caption, date_start=date_start, date_end=date_end, bFilters=bFilters)

@bp.route('/about')
def about():
    return render_template('core/about.html')

@bp.route('/testpage')
def testpage():
    return render_template('core/testpage.html')

'''
@bp.route('/test')
def get_test_image():
    """Just show one image as a test."""

    # filename = "/home/rte/data/images/web/120k/5478268.jpg"
    # images = [url_for("static", filename="/all/7732085.jpg")]
    images = ["7732085"]
    return render_template("core/opening.html", images=images, enumerate=enumerate)
'''
