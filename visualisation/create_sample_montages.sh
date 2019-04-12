#!/bin/bash

cd ~/arXiv/src_all/
dest=~/data/paths/months/montage_lists/

for f in ~/data/paths/months/*.txt;
do
  filename="${f##*/}"
  echo "filename "$filename""
  outname="sample_montage_""${filename%.*}"
  echo "outname "$outname""
  # echo $(cat "$f" | shuf -n 256)

  # trick to add [0] at end of each line to only open first image in each document
  list=$(cat "$f" | sed -e 's/$/[0]/' | shuf -n 72)
  # read a random selection of paths from file
  # list=$(cat "$f" | shuf -n 72)

  echo "$list"
  echo "$list" > "$outname".txt

  # montage command with filename and dimensions, wider grid
  # montage ${list} -colorspace sRGB -units PixelsPerInch -density 300 -background white -alpha off -geometry 320x160+10+10 -pointsize 4 -set label '%f\n%wx%h' "$outname".jpg
  # montage $(head -1 "$f") "$outname"

  # montage command with smaller, more square images
  montage ${list} -colorspace sRGB -units PixelsPerInch -density 300 -background white -alpha off -geometry 240x240+2+2 -tile 12x "$outname"_wide.jpg
  # -label '%f'
done
