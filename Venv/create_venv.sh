#!/bin/bash
# this script creates a Python 2 virtual environment with the necessary packages for the spiderbot
path='./PY2/'
set -e
set -o pipefail
virtualenv -p python2 "$path"
source "$path"'/bin/activate'
pip install --upgrade numpy pygame opencv-python
deactivate
