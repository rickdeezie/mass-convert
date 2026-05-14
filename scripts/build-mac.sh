#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  elif command -v python3.12 >/dev/null 2>&1; then
    PYTHON_BIN="python3.12"
  else
    echo "Could not find Python. Create .venv first or set PYTHON_BIN." >&2
    exit 1
  fi
fi

"$PYTHON_BIN" -m PyInstaller \
  --name "PDF to JPG Converter" \
  --windowed \
  --onedir \
  --clean \
  --noconfirm \
  pdf_to_jpg_converter.py

echo "Built dist/PDF to JPG Converter.app"
