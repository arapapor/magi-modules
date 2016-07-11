#!/bin/bash
#delete magi-modules
echo ~-~-~Deleting Magi-Modules~-~-~
rm -r -f magi-modules

git clone https://github.com/arapapor/magi-modules
cd

cp magi-modules/updateGit.sh ~/
cp magi-modules/runMagi.sh ~/
cp magi-modules/runMagi.txt ~/
