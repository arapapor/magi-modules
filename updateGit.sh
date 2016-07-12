#!/bin/bash
#delete magi-modules
echo ~-~-~Deleting Magi-Modules~-~-~
rm -r -f magi-modules

git clone https://github.com/arapapor/magi-modules
cd

for line in ~/magi-modules/sh.txt; do
  cp $line ~/$line
done


