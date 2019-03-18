#!/bin/bash

srcdir="/mnt/hd-4tb/arXiv/src_all/1001/"
destdir="/home/rte/data/images/1001/"
imagepaths="/home/rte/data/paths/image_paths_1001.txt"
linecount=1

echo "srcdir: $srcdir"
echo "destdir: $destdir"

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
