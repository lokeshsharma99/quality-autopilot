#!/bin/bash

############################################################################
#
#    Quality Autopilot — Virtual Environment Setup
#
#    Usage: ./scripts/venv_setup.sh
#
############################################################################

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${CURR_DIR}")"
VENV_DIR="${REPO_ROOT}/.venv"

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}▸${NC} ${BOLD}Setting up virtual environment${NC}"
echo ""

if [ -d "${VENV_DIR}" ]; then
    echo -e "${DIM}> Removing existing .venv${NC}"
    rm -rf "${VENV_DIR}"
fi

echo -e "${DIM}> python3 -m venv ${VENV_DIR}${NC}"
python3 -m venv "${VENV_DIR}"

echo -e "${DIM}> Activating venv${NC}"
source "${VENV_DIR}/bin/activate"

echo -e "${DIM}> pip install uv${NC}"
pip install uv --quiet

echo -e "${DIM}> uv pip sync ${REPO_ROOT}/requirements.txt${NC}"
uv pip sync "${REPO_ROOT}/requirements.txt"

echo ""
echo -e "${BOLD}Done. Activate with: source .venv/bin/activate${NC}"
echo ""
