#!/bin/bash
# Start magi_orchestrator.py
base="~/magi-modules/"

echo ~-~-~Reading form runMagi.txt~-~-~
#read path read fname read exp read gen <~/runMagiGenerator.txt

#echo $path $fname $exp

path="FileCreator"
fname="FileCreator.aal"
exp="calcaar"
gen="~/users/arapapor/magi-modules/cagent
echo ~-~-~Running magi_orchestrator.py~-~-~
# CHANGE THE BELOW PATH
cd $base$path
magi_orchestrator.py -p montage -e $exp -f $fname


cd $gen
magi_orchestrator.py -p montage -e $exp -f math.aal
