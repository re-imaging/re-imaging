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
from flask import current_app
# from werkzeug.security import check_password_hash
# from werkzeug.security import generate_password_hash

from imagemesh.db import get_db

from annoy import AnnoyIndex

import numpy as np
import random
import math
from datetime import date
import time

from guppy import hpy
h = hpy()
print(h.heap())

# now set in config
# NUM_INDEXES = 600000
# NIMAGES = 50 # 100

bp = Blueprint("core", __name__) # url_prefix="/core"

@bp.route("/", methods=["GET", "POST"])
def get_images():
    """If the user has selected an image, grab annoy results.
    Otherwise grab random images from the database and display.
    """

    filepaths = []

    start = time.time()

    # image_list = "/home/rte/data/paths/600k_from_all_images_shuf.txt"
    image_list = current_app.config['IMAGE_LIST']
    # image_list = url_for("static/600k_from_all_images_shuf.txt")
    filepaths = []

    with open(image_list, "r") as f:
        lines = f.readlines()
        print("length of image text file:",len(lines))
    for l in lines[:current_app.config["NUM_INDEXES"]]:
        substring = l.split(".jpg")[0]
        filepaths.append(substring)

    print(f'getting filepaths from text file, time taken {time.time() - start}')

    ##### get filepaths from DB (slower than text file)
    # start = time.time()
    #
    # db = get_db()
    # c = db.cursor()
    #
    # c.execute("SELECT id FROM single")
    # rows = c.fetchall()
    # filepaths = [str(x[0]) for x in rows]
    # print("number of image paths loaded:", len(filepaths))
    #
    # print(f'getting filepaths from db, time taken {time.time() - start}')

    messages = []

    search_mode = request.form.get("search-mode")
    print(f'search_mode: {search_mode}')

    search_select = request.form.get("search_select")
    print(f'search_select: {search_select}')
    embedding = request.form.get("embedding")
    print("embedding:", embedding)
    image_id = request.form.get("image_id")
    print("image_id:", image_id)

    fts = request.form.get("fts")
    if fts == "":
        fts = None
    print(f'fts: {fts}')

    # filters
    category = request.form.get("category")
    print("category:",category)
    category_name = request.form.get("category-name")
    print("category_name:",category_name)
    # category = set_param(request.form.get("category"), request.args.get('category'))
    # print("category:",category)
    # category_name = set_param(request.form.get("category-name"), request.args.get('category_name'))
    # print("category_name:",category_name)
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

    # compare start and end and swap (or give error) if one before the other
    if date_start and date_end:
        ds = date.fromisoformat(date_start)
        de = date.fromisoformat(date_end)
        if ds > de:
            print("start date earlier than end date! swapping dates")
            tmp = date_start
            date_start = date_end
            date_end = tmp
            messages.append("Start date after end date - selection has been swapped")

    # if there is either a start or end, extend range to max
    if date_start and not date_end:
        date_end = "2020-06-30"
    if date_end and not date_start:
        date_start = "1990-01-17"

    # abstract = request.form.get("abstract")
    # print("abstract:",abstract)
    # identifier = request.form.get("identifier")
    # print("identifier:",identifier)


    filter_arguments = {}

    if category_name:
        filter_arguments["cat"] = f'LIKE "{category_name}%"'
    elif category:
        filter_arguments["cat"] = f'LIKE "{category}%"'
    if imageformat: filter_arguments["imageformat"] = f'LIKE "{imageformat}%"'
    if prediction: filter_arguments["vggpred"] = f'LIKE "{prediction}%"'
    if author: filter_arguments["authors"] = f'LIKE "%{author}%"'
    if title: filter_arguments["title"] = f'LIKE "%{title}%"'
    if creator: filter_arguments["creator"] = f'LIKE "%{creator}%"'
    if caption: filter_arguments["caption"] = f'LIKE "%{caption}%"'
    if date_start: filter_arguments["created"] = f'BETWEEN "{date_start}" AND "{date_end}"'

    # if abstract: filter_arguments["metadata.abstract"] = f'LIKE "%{abstract}%"'
    # if identifier: filter_arguments["metadata.identifier"] = f'LIKE "{identifier}%"'

    # if no selected image, just get random indexes
    # else use annoy to find indexes
    # then filter using SQLite search
    # then get metadata for each image

    # use random search mode
    if search_mode == None or search_mode == "random" or image_id == None or image_id == "":
        print("image_id:", image_id, "- getting random indexes")
        images = copy.deepcopy(filepaths) # only shuffle the copy
        random.shuffle(images)

        image_id = None
        embedding = None
        result_total = None
        images_shown = current_app.config["NIMAGES"]

        if search_mode == "nn":
            if image_id == None or image_id == "":
                messages.append("Error: no image selected for nearest neighbour search - showing randomly sampled images")

    # use nn search mode
    else: # request.method == "POST":
        print("--- nearest neighbours search ---")
        print("image id:", image_id)
        print(f'get annoy indexes for {embedding} and pull images')

        start = time.time()

        ann = AnnoyIndex(300, 'angular')

        if embedding == "VGG16":
            ann_filepath = current_app.config['ANNOY_VGG']
        elif embedding == "raw":
            ann_filepath = current_app.config['ANNOY_RAW']
        elif embedding == "ternary":
            ann_filepath = current_app.config['ANNOY_TERNARY']
        elif embedding == "cats":
            ann_filepath = current_app.config['ANNOY_CATS']

        print(h.heap())
        ann.load(ann_filepath)
        print(h.heap())

        print(f'loading AnnoyIndex, time taken {time.time() - start}')

        start = time.time()

        nindexes = current_app.config["NIMAGES"]
        # if author or category or imageformat or prediction:
        if len(filter_arguments) > 0 or fts:
            nindexes = current_app.config["NUM_INDEXES"]

        target_index = filepaths.index(image_id)
        print(f'getting indexes for image id: {image_id} + target_index: {target_index}')
        indexes = ann.get_nns_by_item(target_index, nindexes)
        # print(f'indexes total {len(indexes)}: {indexes}')

        images = np.array(filepaths)[np.array(indexes)]
        print("target_images:", len(images))
        # print(images)

        print(f'getting indexes, time taken {time.time() - start}')

        result_total = None
        images_shown = current_app.config["NIMAGES"]

    sql_filter = """
                SELECT id
                FROM single
                """

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

    filter_results = []
    fts_results = []

    if filter_count != 0 or fts != None:

        if filter_count != 0:
            print("--- filtering results ---")
            start = time.time()

            print("--- there are filter arguments, running filter")
            db = get_db()
            c = db.cursor()

            c.execute(sql_filter, )
            rows = c.fetchall()

            filter_results = [row[0] for row in rows]
            print(f'querying SQLite for search terms, time taken {time.time() - start}')
            print("filter_results:", len(filter_results))

        if fts != None:
            print("--- running full text search ---")
            start = time.time()

            db = get_db()
            c = db.cursor()

            c.execute("SELECT id FROM vsingle WHERE vsingle MATCH ?", (f'"{fts}"', ))
            rows = c.fetchall()

            fts_results = [row[0] for row in rows]

            print(f'fts results: {len(fts_results)}')
            print(f'running full text search, time taken {time.time() - start}')

        start = time.time()

        # all_results = filter_results + fts_results
        # all_results = list(dict.fromkeys(all_results)) # remove duplicates

        # attempt at making it intersect only
        # check if only one of the filters being used and set
        all_results = []
        if not filter_results and fts_results:
            all_results = fts_results
            if category:
                messages.append("No images found to match filters, showing full text search results")
        elif not fts_results and filter_results:
            all_results = filter_results
            if fts:
                messages.append("No images found to match full text search, showing filter results")
        else:
            # if both, get the intersection
            all_results = np.intersect1d(fts_results, filter_results)

        result_total = len(all_results)

        print(f'cross matching results, time taken {time.time() - start}')

        print("filtering for matches")
        start = time.time()

        matches = []
        for im in images[:]: # NIMAGES
            # print("image:", type(im), im)
            # if np.any(np.array(filter_results) == im):
            if len(matches) >= current_app.config["NIMAGES"]:
                break

            if int(im) in all_results:
                matches.append(im)

        print("len(matches):", len(matches))
        images = matches[:current_app.config["NIMAGES"]]
        images_shown = len(images)

        if images_shown == 0:
            messages.append("Error: no images found that match the requested filters")

        print(f'filtering for matches, time taken {time.time() - start}')

    print("getting metadata for displayed images")
    start = time.time()

    images = images[:current_app.config["NIMAGES"]]

    # only run the below code if we haven't already grabbed the database stuff?
    db = get_db()
    c = db.cursor()
    metadict = {}

    # meta_sql = """
    #             SELECT images.identifier, filename, x, y, imageformat, creator,
    #             metadata.created, metadata.cat, metadata.authors, metadata.title,
    #             images.vggpred, captions.caption, images.id
    #             FROM images
    #             LEFT JOIN metadata ON images.identifier == metadata.identifier
    #             LEFT JOIN captions ON images.caption == captions.id
    #             WHERE images.id IS ?
    #             """

    meta_sql = """
                SELECT identifier, filename, x, y, imageformat, creator,
                created, cat, authors, title,
                vggpred, caption, id
                FROM single
                WHERE id IS ?
                """

    for i in images:
        # print("i:",i)
        c.execute(meta_sql, (i,))
        rows = c.fetchall()
        for row in rows:
            items = [str(r) for r in row]
            # print(items)

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

            cap = rows[0][11]
            if cap is None:
                md["caption"] = "-"
            else:
                md["caption"] = str(cap).replace('\n', ' ')
            # md["caption"] = str(rows[0][11]).replace('\n', ' ')

            meta_image_id = str(rows[0][12])
            metadict[meta_image_id] = md
    print("metadict length:", len(metadict))

    print(f'querying metadata, time taken {time.time() - start}')

    # images_shown = None
    # if result_total:
    #     images_shown = min(images_shown, result_total)
    print("images_shown:", images_shown)

    si_meta_d = {}

    if image_id:
        c.execute(meta_sql, (image_id,))
        rows = c.fetchall()

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
        # print("earlier caption:", rows[0][11])
        cap = rows[0][11]
        if cap is None:
            md["caption"] = "-"
        else:
            md["caption"] = str(cap).replace('\n', ' ')
        # md["caption"] = str(rows[0][11]).replace('\n', ' ')

        meta_image_id = str(rows[0][12])
        si_meta_d[image_id] = md

    # check if we have filters, pass number to template
    nFilters = 0
    if len(filter_arguments) > 0:
        nFilters = len(filter_arguments) # True

    print(h.heap())
    print(f'calling return render_template, with {len(images)} images: {images}')
    return render_template('core/interface.html.j2', images=images, metadict=metadict,
                            enumerate=enumerate, prev_image_id=image_id, result_total=result_total,
                            images_shown=images_shown, embedding=embedding, search_select=search_select,
                            si_meta_d=si_meta_d,
                            category=category, category_name=category_name, imageformat=imageformat, prediction=prediction, author=author,
                            title=title, creator=creator, caption=caption, date_start=date_start, date_end=date_end, nFilters=nFilters, messages=messages, fts=fts)

@bp.route('/about')
def about():
    return render_template('core/about.html')
