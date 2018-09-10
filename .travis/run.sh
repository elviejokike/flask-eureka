#!/bin/bash

set -e
set -x

python setup.py bdist_wheel
python setup.py sdist
