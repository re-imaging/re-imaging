#!/bin/bash

# script that runs a find command from a target directory and
# creates a text file with all of the file paths
# this was then used to run commands over each file in order

# arguments
# 1 - source directory to run find from
# 2 - target text file to write paths

set -o nounset
set -o errexit

if [ "$1" != "" ]; then
  echo "source directory: "$1""
  srcdir="$1"
fi

if [ "$2" != "" ]; then
  echo "target file to write: "$2""
  destfile="$2"
fi

cd "$srcdir"
echo "current working directory: "$(pwd)""

count=0

find . -type f \( -iname "*.png" -o -iname "*.eps" -o -iname "*.pdf" -o -iname "*.ps" -o -iname "*.jpg" \
-o -iname "*.jpeg" -o -iname "*.pstex" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.epsf" \) \
-not -name "*pdf_image-*" | while read fullpath; do

  # echo "--------------------"
  echo "$fullpath"

  article="$(cut -d'/' -f3 <<< "$fullpath")"
  # path="${fullpath%/*}"
  name="${fullpath##*/}"
  # echo $path
  # echo $name
  # echo "$article"

  pdfext=$article
  # *_${article}.pdf
  # echo ${article}.pdf
  pdfarticle="${article}.pdf"
  # echo $pdfarticle
  # echo "----------"
  if [[ $name != $pdfarticle && $name != "article.pdf" ]];
  then
    count=$((count+1))
    echo $count
    # if [[ $count > 20 ]]; then exit 1; fi
    # echo "---------- processing article"
    # filesize=$(stat --printf="%s" "$fullpath")
    # echo $filesize
    # res="$(identify -ping -format "%w %h %m" "$fullpath")"
    # echo $res
    # x="$(cut -d' ' -f1 <<< "$res")"
    # echo $x
    # y="$(cut -d' ' -f2 <<< "$res")"
    # echo $y
    # imageformat="$(cut -d' ' -f3 <<< "$res")"
    # echo $imageformat

    # sqlite3 /home/rte/data/db/arxiv_db_test.sqlite3 "INSERT INTO images \
    # (identifier, filename, filesize, path, x, y, imageformat) \
    # VALUES (\"$article\", \"$name\", \"$filesize\", \"$path\", \"$x\", \"$y\", \"$imageformat\");"
    # destfile=~/data/paths/all_image_paths.txt
    echo "$fullpath" >> "$destfile"
  fi
  echo "total number of files:"
  echo $count
done
