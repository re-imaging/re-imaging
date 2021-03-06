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
import datetime
import signal
# import subprocess
# import concurrent.futures
# from functools import partial
# import itertools
# import math

parser = argparse.ArgumentParser(description='Script for getting captions from .tex files')

parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('tex_list', help="path to file that stores list of all .tex files")
parser.add_argument('--start_line', default=0, type=int, help='line to read textfile from (default: 0)')
# parser.add_argument('--end_line', default=0, type=int, help='line to read textfile from (default: 0)')
# parser.add_argument('-s', '--slice_size', default=2500, type=int, help='size of each slice to process (default: 2500)')
# parser.add_argument('-n', '--num_threads', default=8, type=int, help='number of threads (default: 8)')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-t', '--timing', action='store_true', help='timing output')
parser.add_argument('-z', '--dryrun', action='store_true', help="don't modify the database, just print (default: False)")
parser.add_argument('-r', '--shuffle', action='store_true', help="shuffle the list of tex files (default: False)")

global args
args = parser.parse_args()

db = sqlite3.connect(args.db_path)
c = db.cursor()

now = datetime.datetime.now()
now_string = "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
logpath = "error_log_" + now_string + ".txt"

id_re = r'\/(\d{4}\.\d{4,5}|[^\/]+?\d{7})\/'
caption_re = r'(?:\\caption[^{]*?{)(?:\s?\\label{[\S\s]*?\})?\s?([\s\S]+?)(?:\s+?\}?\s?)?(?:(?:\s*?\}?\s*?\\label)|(?:\}\s*?\\end))'
# label_re = r'(?:\\caption[\s\S]*?)(?:\\label\{)([^}]+?)(?:\})'
label_re = r'(?:\\label\{)([^}]+?)(?:\})'
imagecheck_re = r'(?:\\epsfbox|\\sfig|\\plotfiddle|\\plottwo|\\psfig|\\plotone|\\includegraphics|\\epsfig)[^\{]*?(?:\{file=|\{figure=|{)([^\}\,]+)'
subfigure_re = r'\\begin\{subfigure[\S\s]+?\\end\{subfigure\}'
remove_label_re = r'\s*\\label\{[^\}]*?\}\s*'

def handler(signum, frame):
    print("timeout!")
    raise Exception("end of time")

def parse_caption(text):
    offset = 0
    level = 0
    sq_level = 0
    completed_braces = False
    first_brace = text.find("{")
    first_sq_bracket = text.find("[")
    if first_sq_bracket != -1:
        start = min(first_brace, first_sq_bracket)
    else:
        start = first_brace

    end = 2000 # arbitrary
    offset = 0
    # print("parsing caption from start:", start)
    # print("skipping first part of string:", text[:start])

    for i, char in enumerate(text[start:]):
        # print(char, end=" ")
        if char == "{":
            level += 1
            if level == 1:
                offset = i
        if char == "}":
            level -= 1
            if sq_level == 0:
                completed_braces = True
        if char == "[":
            sq_level += 1
        if char == "]":
            sq_level -= 1

        if level == 0 and sq_level == 0 and completed_braces == True:
            # print("end loop")
            end = i
            return text[start+offset+1:start+end]
#         else:
#             print("continue loop")

    return text[start+1:]

def check_caption(text):
    start_index = 0
    found_caption = False

    while found_caption is False:
        start_index = text.lower().find(r"\caption", start_index)
#         print("start_index:",start_index)
        if start_index == -1:
            if args.verbose:
                print(text)
                print("COULDN'T FIND ANOTHER \caption")
#             start_index = text.lower().find(r"\mycaption")
            return ""
            break
        if text.lower()[start_index:].startswith(r"\captionsetup"):
#             print("found \captionsetup -> increment start_index")
            start_index += 5
        else:
#             print("found a caption")
            found_caption = True
    return text[start_index:]

def get_caption(t):
    signal.alarm(10)

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

            if args.verbose:
                print(t)

            match = re.search(id_re, t)
            if match:
                article_id = match.group(1)
            elif(args.verbose):
                print("!!! no article id found!")
            # print(article_id)

            # extract figure text from (La)TeX file
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
            # remove all subfigures
#             print("-" * 15)
            figure_text = re.sub(subfigure_re, "", figure[2])
#             print("figure_text", figure_text)

            caption_text = check_caption(figure_text)

#             print("-" * 15)
            start_index = figure_text.find(r'\caption')
#             print("start_index:", start_index)
            caption = parse_caption(caption_text)
            # print(">>>>> caption:")
            # print(caption)

            # remove labels from caption
            caption = re.sub(remove_label_re, "", caption)
            # print(">>>>> caption w labels removed:")
            # print(caption)
            figures[i].append(caption)

            # get label
            match = re.search(label_re, figure_text)
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

            if args.verbose:
                print(figures[i])

            # data.append(figure)
        if args.dryrun is False:
            for identifier, fignum, _, caption, label, filenames in figures:
                c.execute("INSERT INTO captions (identifier, tex, fignum, caption, label, filenames) \
                VALUES (?, ?, ?, ?, ?, ?)", \
                (identifier, t, fignum, caption, label, ','.join([str(elem) for elem in filenames])))
            db.commit()

        signal.alarm(0)
        return 0

    except UnicodeDecodeError as error:
        print("decode error!",error)
        with open(logpath, "a+") as f:
            f.write(t + "\n")
        # global error_count += 1

    except KeyboardInterrupt:
        db.commit()
        with open(logpath, "a+") as f:
            f.write(t + "\n")
        # quit
        sys.exit()

    except Exception as e:
        db.commit()
        with open(logpath, "a+") as f:
            f.write(t + "\n")
        raise e
    # finally:

def main():
    signal.signal(signal.SIGALRM, handler)

    start = time.time()

    texs = []
    with open(args.tex_list) as f:
        texs = json.load(f)

    # if(args.verbose):
    print("loaded file of .tex paths")
    print(len(texs))

    end = time.time()
    print("time taken to load entries:",end-start)
    start = time.time()

    if args.shuffle:
        print(">>> shuffling tex file list")
        random.seed(5)
        random.shuffle(texs)

        end = time.time()
        print("time taken to shuffle entries:",end-start)
        start = time.time()

    for ai, t in enumerate(texs[args.start_line:]):
        if(args.verbose):
            print("*" * 20)
            print("paper:",ai)
            # print("-" * 20)
        get_caption(t)
        if ai % 1000 == 0:
            print("*" * 20)
            print("texs:",ai)

            end = time.time()
            print("time taken for process:",end-start)
            start = time.time()

if __name__ == "__main__":
    main()
