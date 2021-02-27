#!/bin/bash

# script that reads in a text file of image paths and identifiers,
# then writes image data into a SQLite database using the identify command

cd ~/src_update
# cd ~/arXiv/src_all
echo "current working directory: "
pwd

startline=0
count=0
db="~/data/db/arxiv_db_images.sqlite3"

if [ "$1" != "" ]; then
  echo "reading from line "$1""
  startline=$1
  count=$1
fi

if [ "$2" != "" ]; then
  echo "target file to read: "$2""
  targetfile="$2"
fi

if [ "$3" != "" ]; then
  echo "database file: "$3""
  db="$3"
fi

tail -n +${startline} $targetfile | while read fullpath; do

  echo "--------------------"
  # echo "$fullpath"
  # fullpath=${fullpath#"."} # remove the first full stop, if there is one
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

    sqlite3 "$db" "INSERT INTO images \
    (identifier, filename, filesize, path, x, y, imageformat) \
    VALUES (\"$article\", \"$name\", \"$filesize\", \"$path\", \"$x\", \"$y\", \"$imageformat\");"
  fi
done
