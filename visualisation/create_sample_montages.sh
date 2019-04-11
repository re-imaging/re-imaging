#!/bin/bash

cd ~/arXiv/src_all/

for f in ~/data/paths/months/*.txt;
do
  filename="${f##*/}"
  echo "filename "$filename""
  outname="sample_montage_""${filename%.*}".jpg
  echo "outname "$outname""
  # echo $(cat "$f" | shuf -n 256)
  montage $(cat "$f" | shuf -n 256) -colorspace sRGB -units PixelsPerInch -density 300 -background white -alpha off "$outname"
  # montage $(head -1 "$f") "$outname"
done
