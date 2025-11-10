#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

# Pick a Python command that exists
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
elif command -v py >/dev/null 2>&1; then
  PY="py -3"
else
  echo "❌ Python not found. Install Python 3 and try again."
  exit 1
fi

# Create venv only if missing
if [ ! -d "$VENV_DIR" ]; then
  eval $PY -m venv "$VENV_DIR"
fi

# Activate (Linux/Mac = bin; Windows = Scripts)
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV_DIR/Scripts/activate"
else
  echo "❌ Could not find activate script in $VENV_DIR"
  exit 1
fi

# Upgrade pip
python -m pip install --upgrade pip

# Install deps if present
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  echo "ℹ️ No requirements.txt — skipping"
fi

echo "✅ Environment Ready"
