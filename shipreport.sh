#!/bin/bash
echo "Running Ship Report Maker"
echo $PATH
cd /fel
source felenv/bin/activate
python3 shipreport.py

