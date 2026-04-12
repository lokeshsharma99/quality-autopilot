#!/bin/bash

############################################################################
#
#    Quality Autopilot — Validate
#
############################################################################

set -e

echo "Running ruff check..."
ruff check .

echo "Running mypy..."
mypy . --ignore-missing-imports

echo "All checks passed."
