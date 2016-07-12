#!/bin/bash
#delete magi-modules
echo ~-~-~Deleting Magi-Modules~-~-~
rm -r -f magi-modules

git clone https://github.com/arapapor/magi-modules
cd

path=$( cat ~/magi-modules/sh.txt )


for line in $path; do
  cp ~/magi-modules/$line ~/$line
done


