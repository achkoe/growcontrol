#! /usr/bin/bash

source /home/pi/venv/vgc/bin/activate
export PYTHONPATH=/home/pi/growcontrol
cd /home/pi/growcontrol
python watchdog.py 
