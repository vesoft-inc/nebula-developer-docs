#!/bin/sh
set -eu
# Run inside a virtual environment; no system packages or sudo required.
python -m pip install -r requirements-preview.txt
