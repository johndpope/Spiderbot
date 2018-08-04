#!/bin/bash
# run this script to start the spiderbot in the virtual environment Venv
set -e
set -o pipefail
source 'Venv/PY2/bin/activate'
python spiderbot.py
deactivate
