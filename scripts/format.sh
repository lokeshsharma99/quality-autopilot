#!/bin/bash

############################################################################
#
#    Quality Autopilot — Format
#
############################################################################

set -e

echo "Running ruff format..."
ruff format .

echo "Running ruff check --fix..."
ruff check --fix .

echo "Done."
