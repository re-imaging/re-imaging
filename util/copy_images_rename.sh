#!/bin/bash

# script to copy files from a source to destination folder
# uses a text file with file paths
# renames folders according to their line number in the file paths text file

# arguments
# 1 - source directory
# 2 - target directory
# 3 - text file containing image paths

set -o nounset
set -o errexit

if [ "$1" != "" ]; then
  echo "source directory: "$1""
  srcdir="$1"
fi

if [ "$2" != "" ]; then
  echo "target directory: "$2""
  destdir="$2"
fi

if [ "$3" != "" ]; then
  echo "text file containing image paths: "$3""
  imagepaths="$3"
fi

# srcdir="/mnt/hd-4tb/arXiv/src_all/1001/"
# destdir="/home/rte/data/images/1001/"
# imagepaths="/home/rte/data/paths/image_paths_1001.txt"
linecount=1

echo "srcdir: "$srcdir""
echo "destdir: "$destdir""
echo "imagepaths: "$imagepaths""

cd $srcdir
pwd

cat "$imagepaths" | while read f; do
  echo "linecount: "$linecount""
  echo "copying "$f""
  cp "$f" $destdir
  cpname="$destdir${f##*/}"
  echo "cpname: "$cpname""
  ext=${f##*.}
  echo "ext "$ext""
  num=$(printf "%08d" $linecount)
  newf="$destdir$num.$ext"
  echo "new filename: "$newf""
  mv "$cpname" "$newf"

  linecount=$((linecount+1))
done
