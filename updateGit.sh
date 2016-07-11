#!/bin/bash
#delete magi-modules
echo ~-~-~Deleting Magi-Modules~-~-~
rm -r -f magi-modules
git clone https://github.com/arapapor/magi-modules
for line in sh.txt; do 
  fname = "magi-modules"
  cp $fname/$line ~/
  done 
cd

#cp magi-modules/updateGit.sh ~/
#cp magi-modules/runMagi.sh ~/
