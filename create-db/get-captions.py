#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
import json
import sqlite3
import random
import time
import argparse
# import subprocess
# import concurrent.futures
# from functools import partial
# import itertools
# import math

parser = argparse.ArgumentParser(description='Script for getting captions from .tex files')

# db_path = "/home/rte/data/db/arxiv_db.sqlite3"
parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('tex_list', help="path to file that stores list of all .tex files")
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
# parser.add_argument('-s', '--slice_size', default=2500, type=int, help='size of each slice to process (default: 2500)')
# parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
# parser.add_argument('-t', '--timing', action='store_true', help='timing output')
# parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify or create any files (default: False)")

global args
args = parser.parse_args()

# article_count = 0
# figure_count = 0
# error_count = 0

def get_caption(t, db, c):

    id_re = r'\/(\d{4}\.\d{4,5}|[^\/]+?\d{7})\/'
    caption_re = r'(?:\\caption[^{]*?{)(?:\s?\\label{[\S\s]*?\})?\s?([\s\S]+?)(?:\s+?\}?\s?)?(?:(?:\s*?\}?\s*?\\label)|(?:\}\s*?\\end))'
    label_re = r'(?:\\caption[\s\S]*?)(?:\\label\{)([^}]+?)(?:\})'
    imagecheck_re = r'(?:\\epsfbox|\\sfig|\\plotfiddle|\\plottwo|\\psfig|\\plotone|\\includegraphics|\\epsfig)[^\{]*?(?:\{file=|\{figure=|{)([^\}\,]+)'

    data = []

    try:
        with open(t, "rt", encoding="latin1") as f:
    #             print(f)
            article_data = []
    #             content = [x.strip() for x in f.readlines()]
            content = f.readlines()

            # global article_count += 1
            start = 0
            end = 0

            fignum = 1 # 1 indexed figures, i.e. no figure 0
            figures = []

            print(t)
            match = re.search(id_re, t)
            if match:
                article_id = match.group(1)
            elif(args.verbose):
                print("!!! no article id found!")
            # print(article_id)

            # iterate over each line and find where a figure begins
            for i, l1 in enumerate(content[:]):
                if r"\begin{figure" in l1 and l1.lstrip().startswith("%") is False:
                    start = i
                    # found a figure, now create our row of data
                    article_data.append(article_id)
                    article_data.append(fignum)

                    figures.append([article_id, fignum, ""])

                    # find where figure ends
                    for j, l2 in enumerate(content[i:]):
                        if l2.lstrip().startswith("%") is False:
    #                             print(l2)
                            figures[fignum-1][2] += l2 # 1 indexed figures, i.e. no figure 0

                            if r"\end{figure" in l2:
                                end = start + j
                                break
                    # global figure_count += 1
                    fignum += 1
                    # counter += 1

        # organise and print data
        for i, figure in enumerate(figures):
            # print("article-id:",figure[0])
            # print("fignum:",figure[1])
            # print("figure text:")
            # print(figure[2])

            # get caption
            match = re.search(caption_re, figure[2])
            if match:
                # print("caption:")
                # print(match.group(1))
                figures[i].append(match.group(1))
            else:
                # print("!!! no caption")
                figures[i].append("")
            # get label
            match = re.search(label_re, figure[2])
            if match:
                # print("label:",match.group(1))
                figures[i].append(match.group(1))
            else:
                figures[i].append("")
                # print("!!! no label")
            # get filenames
            filenames = re.findall(imagecheck_re, figure[2])
            # print("filenames:",filenames)
            figures[i].append(filenames)
            # print("-" * 30)
            # print("")

            # data.append(figure)

        for identifier, fignum, _, caption, label, filenames in figures:
            c.execute("INSERT INTO captions (identifier, fignum, caption, label, filenames) \
            VALUES (?, ?, ?, ?, ?)", \
            (identifier, fignum, caption, label, ','.join([str(elem) for elem in filenames])))
        db.commit()

    except UnicodeDecodeError as error:
        print("decode error!",error)
        # global error_count += 1

    except KeyboardInterrupt:
        db.commit()
        # quit
        sys.exit()

    except Exception as e:
        raise e
    # finally:

def main():
    db = sqlite3.connect(args.db_path)

    c = db.cursor()

    start = time.time()

    texs = []
    with open(args.tex_list) as f:
        texs = json.load(f)

    if(args.verbose):
        print("loaded file of .tex paths")
        print(len(texs))

    end = time.time()
    print("time taken to load entries:",end-start)
    start = time.time()

    # article_count = 0
    # figure_count = 0
    # error_count = 0

    for ai, t in enumerate(texs[:]):
        if(args.verbose):
            print("*" * 20)
            print("paper:",ai)
            print("-" * 20)
        get_caption(t, db, c)

    end = time.time()
    print("time taken for process:",end-start)
    start = time.time()

    # [r.pop(2) for r in data]

    # print("*" * 20)
    # print("error_count:",error_count)
    # print("article_count:",article_count)
    # print("figure_count:",figure_count)
    # print("*" * 20)
    # print(data)

if __name__ == "__main__":
    main()
