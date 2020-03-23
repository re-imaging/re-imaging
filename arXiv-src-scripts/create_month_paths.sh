#!/bin/bash

# NB: see image_paths_to_txt.sh instead

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
  echo -e "Usage:\n ./create_month_paths.sh [source directory]"
}

# if less than two arguments supplied, display usage
if [ $# -le 0 ]
then
  echo "not enough arguments"
  display_usage
  exit 1
fi

# check whether user had supplied -h or --help . If yes display usage
if [[ ( $# == "--help") ||  $# == "-h" ]]
 then
   echo "help"
   display_usage
   exit 0
 fi

if [ "$1" != "" ]; then
  echo "checking if "$1" is a directory"
  if [[ -d "$1" ]]; then
    echo "source directory: "$1""
    srcdir="$1"
  fi
fi

cd "$srcdir"
echo "current directory: $(pwd)"

# add slash at the end to only find directories
for m in */;
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

    echo "--------------------"
    echo "fullpath "$fullpath""

    article="$(cut -d'/' -f2 <<< "$fullpath")"
    # path="${fullpath%/*}"
    name="${fullpath##*/}"
    # echo "path "$path""
    echo "name "$name""
    echo "article "$article""

    ext="${name##*.}"
    echo "extension "$ext""

    multipagepdf=0

    if [[ $ext = "pdf" ]];
    then
      # this checks the pdf file for how many pages it contains
      # we can pretty safely ignore multipage pdf files as they are likely to be whole articles
      echo "opening "$fullpath""
      npages=$(pdfinfo "$fullpath" | grep Pages | awk '{print $2}')
      echo "number of pages: ""$npages"

      if (( npages > 1 ));
      then
        let multipagepdf=1
        echo "multipagepdf $multipagepdf"
      fi
    fi

    # pdfext=$article
    # *_${article}.pdf
    # echo ${article}.pdf

    pdfarticle="${article}.pdf"
    echo "pdfarticle "$pdfarticle""

    if [[ $name != $pdfarticle && $multipagepdf != 1 ]];
    then
      # let "count=count+1"

      # COUNTER=$(($(cat $TEMPFILE) + 1))
      # echo $COUNTER > $TEMPFILE

      # echo "count "$count""
      echo "writing data"
      # the ":1" removes the leading "." which is manually added to the beginning of the path
      echo "./""$month""${fullpath:1}" >> "$dest"
    fi
  done;
  echo "--------- returning to original directory for next loop"
  cd ..
  echo "current directory: "$(pwd)"";
done
