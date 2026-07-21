#!/bin/bash
# GROMACS-GUI Linux Run Script
# Usage: bash run.sh

set -e

echo "==================================="
echo "     GROMACS-GUI Startup (Linux)"
echo "==================================="
echo

# Use venv if present in common location
VENV_PATH="/tmp/gromacs-gui-venv"
if [ -d "$VENV_PATH" ]; then
    echo "[INFO] Activating virtualenv at $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "[INFO] No venv detected, using system python (may need pip install)"
fi

echo
echo "[1/3] Checking Python and dependencies..."
python --version
python -c "import PyQt6; import matplotlib; import numpy; print('✅ PyQt6, matplotlib, numpy OK')"

echo
echo "[2/3] Checking GROMACS..."
if command -v gmx &> /dev/null; then
    gmx --version | head -3
    echo "✅ gmx found in PATH"
else
    echo "⚠️  gmx NOT found in PATH. Please ensure GROMACS is installed and in PATH."
    echo "   (In this test env, a mock gmx is provided for simulation)"
fi

echo
echo "[3/3] Starting GROMACS-GUI..."
echo "   (To run headless tests, use: QT_QPA_PLATFORM=offscreen python src/main.py )"
echo

# Run with offscreen by default for headless envs (user can override)
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}

python src/main.py
