#!/usr/bin/env bash
set -e

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

echo "✅ Environment Ready"
echo "Now create Postgres DB and run Odoo with addons-path pointing to this repo."
