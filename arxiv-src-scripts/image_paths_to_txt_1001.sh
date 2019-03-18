#!/bin/bash

cd ~/arXiv/src_all/1001
echo "current working directory: "
pwd

count=0

find . -type f \( -iname "*.png" -o -iname "*.eps" -o -iname "*.pdf" -o -iname "*.ps" -o -iname "*.jpg" \
-o -iname "*.jpeg" -o -iname "*.pstex" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.epsf" \) \
-not -name "*pdf_image-*" | while read fullpath; do

  # echo "--------------------"
  echo "fullpath "$fullpath""

  article="$(cut -d'/' -f2 <<< "$fullpath")"
  # path="${fullpath%/*}"
  name="${fullpath##*/}"
  echo "path "$path""
  echo "name "$name""
  echo "article "$article""

  # pdfext=$article
  # *_${article}.pdf
  # echo ${article}.pdf
  pdfarticle="${article}.pdf"
  echo "pdfarticle "$pdfarticle""
  # echo "----------"
  if [[ $name != $pdfarticle ]];
  then
    count=$((count+1))
    echo "count "$count""
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
    destdir=~/data/paths/image_paths_1001.txt
    echo "$fullpath" >> "$destdir"
  fi
done
# echo "total number of files:"
# echo $count
