#!/bin/bash

# this script moves to each subfolder, runs a find command, and then creates
# a matching text file that lists all the relevant paths

# src_all
# ---> 0001
# ---> 0002
# ---> ...
# ---> 9912
# 330 folders

# TEMPFILE=/tmp/$$.tmp

display_usage() {
  echo "create_month_paths.sh - make path files from a selection of folders"
  echo -e "\nUsage:\n ./create_month_paths.sh [source directory]"
}

if [ "$1" != "" ]; then
  echo "source directory: "$1""
  srcdir="$1"
fi

cd "$srcdir"
echo "current directory: $(pwd)"

for m in *;
do
  cd "$m"
  wd=$(pwd)
  echo "running find for directory: "$wd""
  month=${wd##*/}
  dest=~/data/paths/months/"$month".txt

  # echo 0 > $TEMPFILE

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
      # let "count=count+1"

      # COUNTER=$(($(cat $TEMPFILE) + 1))
      # echo $COUNTER > $TEMPFILE

      # echo "count "$count""

      echo "$fullpath" >> "$dest"
    fi
  done
done
