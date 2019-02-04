#!/bin/bash

# script for extracting the source files for the arxiv database
# files are first downloaded using Amazon Web Services
# see https://arxiv.org/help/bulk_data for more information

# this script processes the downloaded data:
# - extracts the tar archives to folders
# - moves all PDF files to individually named folders
# - gets images from PDF files using pdfimages
# - gets text from PDF files using pdftotext
# - finishes extracting all tar and gz zipped archives
# - moves each text only article to its own individual folder

# after downloading the files, change into directory
cd ~/arXiv/

# for each archive, decompress into a specific folder
for i in src/*; do tar xvf $i -C src_all/; done

# change directory
cd ../src_all

# check how many pdf files there are
echo "total number of pdf only articles: "
find . -maxdepth 2 -name "*.pdf" -print

# move all pdf files to their own folder
find . -maxdepth 2 -name "*.pdf" -print -exec sh -c 'mkdir "${1%.*}" ; mv "$1" "${1%.*}" ' _ {} \;

# do the extraction here as it will operate only on the papers that were given only as pdf
# extract all images from pdf files
find . -maxdepth 3 -name "*.pdf" -print -exec sh -c 'pdfimages -png "${1}" "${1}_image" ' _ {} \;

# extract text from pdf files
find . -name "*.pdf" -print -exec sh -c 'pdftotext "${1}" "${1%.*}.txt" ' _ {} \;

# for each archive within each subfolder (needed so tar puts things in proper places)
# find all gz tars, extract, and then delete the gz files
for d in *; do cd "$d" && for f in *.gz; do tar xvfz "$f" --one-top-level && rm "$f"; done; cd ..; done

# note that some of the archives are gz only and not tar
# seems to be because they only contain one file
# so for these we use gunzip
find . -name "*.gz" -exec gunzip -v {} \;

# and for each individual (tex) file, make a folder and move the item to that folder
# note this needs to do some trickery as many of these files don't have extensions and we can't make a folder of the same name
find . -maxdepth 2 -type f -exec sh -c 'mkdir "${1}_dir" ; mv "$1" "${1}_dir" ; mv "${1}_dir" "$1"' _ {} \;
