#!/bin/bash
# Start magi_orchestrator.py
base="~/magi-modules/"
'''
echo -----input filename-----
read path
echo -----input file-----
read fname
echo -----input expirement-----
read exp
'''
read path read fname read exp
echo ~-~-~Running magi_orchestrator.py~-~-~
# CHANGE THE BELOW PATH
cd $base$path
magi_orchestrator.py -p montage -e $exp -f $fname
