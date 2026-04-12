#!/bin/bash

############################################################################
#
#    Quality Autopilot — Virtual Environment Setup
#
############################################################################

set -e

echo "Creating virtual environment..."
uv venv .venv --python 3.12

echo "Activating..."
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -e ".[dev]"

echo ""
echo "Done. Activate with: source .venv/bin/activate"
