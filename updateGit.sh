#!/bin/bash
#delete magi-modules
echo ~-~-~Deleting Magi-Modules~-~-~
rm -r -f magi-modules

git clone https://github.com/arapapor/magi-modules
cd

base="magi-modules"

for line in ~/sh.txt; do
  cp $base$line ~/
done

