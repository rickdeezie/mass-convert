#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python}"
SOURCE_DIR="$PROJECT_ROOT/src"
LAUNCHER="$PROJECT_ROOT/pdf_to_jpg_converter.py"

if [[ ! -f "$LAUNCHER" ]]; then
  echo "Could not find pdf_to_jpg_converter.py in $PROJECT_ROOT" >&2
  exit 1
fi

if [[ ! -d "$SOURCE_DIR/pdf_to_jpg_app" ]]; then
  echo "Could not find src/pdf_to_jpg_app in $PROJECT_ROOT" >&2
  exit 1
fi

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

"$PYTHON_BIN" -c "import pymupdf, fitz; print('PyMuPDF import ok')"

"$PYTHON_BIN" -m PyInstaller \
  --name "PDF to JPG Converter" \
  --windowed \
  --onedir \
  --clean \
  --noconfirm \
  --paths "$SOURCE_DIR" \
  --collect-all pymupdf \
  --collect-all fitz \
  --hidden-import pymupdf \
  --hidden-import fitz \
  --hidden-import pdf_to_jpg_app.gui \
  --hidden-import pdf_to_jpg_app.converter \
  --hidden-import pdf_to_jpg_app.worker \
  "$LAUNCHER"

echo "Built dist/PDF to JPG Converter.app"
