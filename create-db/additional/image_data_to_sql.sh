#!/bin/bash

cd ~/arXiv/src_all
echo "current working directory: "
pwd

count=0

# find all relevant image files
find . -type f \( -iname "*.png" -o -iname "*.eps" -o -iname "*.pdf" -o -iname "*.ps" -o -iname "*.jpg" \
-o -iname "*.jpeg" -o -iname "*.pstex" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.epsf" -o -iname "*.epsi" \) \
-not -name "*pdf_image-*" | while read fullpath; do

  echo "--------------------"
  echo "$fullpath"

  article="$(cut -d'/' -f3 <<< "$fullpath")"
  path="${fullpath%/*}"
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

  # check that the filename is not the same as the article ID, indicating a PDF of the article
  if [[ $name != $pdfarticle ]];
  then
    count=$((count+1))
    echo $count
    # if [[ $count > 20 ]]; then exit 1; fi
    # echo "---------- processing article"
    filesize=$(stat --printf="%s" "$fullpath")
    # echo $filesize
    res="$(identify -ping -format "%w %h %m" "$fullpath")"
    # echo $res
    x="$(cut -d' ' -f1 <<< "$res")"
    # echo $x
    y="$(cut -d' ' -f2 <<< "$res")"
    # echo $y
    imageformat="$(cut -d' ' -f3 <<< "$res")"
    # echo $imageformat

    # insert row into sqlite3
    sqlite3 /home/rte/data/db/arxiv_db_test.sqlite3 "INSERT INTO images \
    (identifier, filename, filesize, path, x, y, imageformat) \
    VALUES (\"$article\", \"$name\", \"$filesize\", \"$path\", \"$x\", \"$y\", \"$imageformat\");"
  fi
done
