#!/bin/bash

cd ~/arXiv/src_all
echo "current working directory: "
pwd

startline=0
count=0

if [ "$1" != "" ]; then
  echo "reading from line "$1""
  startline=$1
  count=$1
fi


tail -n +${1} ~/data/paths/all_image_paths.txt | while read fullpath; do

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
  if [[ $name != $pdfarticle && $name != "article.pdf" ]];
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

    sqlite3 /home/rte/data/db/arxiv_db_images.sqlite3 "INSERT INTO images \
    (identifier, filename, filesize, path, x, y, imageformat) \
    VALUES (\"$article\", \"$name\", \"$filesize\", \"$path\", \"$x\", \"$y\", \"$imageformat\");"
  fi
done
