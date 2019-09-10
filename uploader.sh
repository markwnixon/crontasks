#!/bin/bash
echo "Running Main Bins Uploader"
echo $PATH
cd /home/mark/flask
source flaskenv/bin/activate
cd /home/mark/flask/crontasks
python3 jayuploader.py
