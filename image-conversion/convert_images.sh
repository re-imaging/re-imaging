#!/bin/bash

# arguments
# 1 - source directory
# 2 - target directory
# 3 - minimum image size

set -o nounset
set -o errexit

if [ "$1" != "" ]; then
  echo "source directory: "$1""
  srcdir="$1"
fi

if [ "$2" != "" ]; then
  echo "target directory: "$2""
  targetdir="$2"
fi

if [ "$3" != "" ]; then
  echo "min image size "$3""
  minsize="$3"
fi

cd "$srcdir"
echo "current working directory: "
pwd

# ls | while read f

echo "converting files to "$targetdir""

for f in *; do
  # check if f is a regular file
  if [[ -f "$f" ]]; then
    base=${f%.*}
    echo "base "$base""
    echo "f "$f""
    newname="$targetdir/$base.jpg"
    echo "newname "$newname""
    # run the convert command, but continue even if it fails
    convert "$f" -colorspace sRGB -units PixelsPerInch -density 300 -background white -alpha off -resize "$minsize"x"$minsize"^\> "$newname" || true
  fi
done
