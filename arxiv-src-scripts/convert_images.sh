#!/bin/bash

cd ~/data/images/1001/
echo "current working directory: "
pwd

# ls | while read f

for f in *; do
  # check if f is a regular file
  if [[ -f "$f" ]]; then
    base=${f%.*}
    echo "base "$base""
    echo "f "$f""
    newname="converted/$base.jpg"
    echo "newname "$newname""
    convert "$f" -resize "512^>" "$newname"
  fi
done
