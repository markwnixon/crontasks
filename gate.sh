#!/bin/bash
echo "Running Gate Monitor"
echo $PATH
cd /home/mark/flask
source flaskenv/bin/activate
cd /home/mark/flask/crontasks
python3 gatemonitor.py
