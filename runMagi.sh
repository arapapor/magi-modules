#!/bin/bash
# Start magi_orchestrator.py
base="~/magi-modules/"

echo ~-~-~Reading form runMagi.txt~-~-~
read path read fname read exp <~/runMagi.txt

echo $path $fname $exp

echo ~-~-~Running magi_orchestrator.py~-~-~
# CHANGE THE BELOW PATH
cd $base$path
magi_orchestrator.py -p montage -e $exp -f $fname



