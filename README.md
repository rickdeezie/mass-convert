# PDF to JPG Converter

A small desktop utility for batch converting local PDF scans to JPG images.

The app lets a user select PDF files or an input folder, choose an output folder, set DPI and JPEG quality, and convert the files without uploading them anywhere.

## Mac setup for testing

Use Python 3.12 or 3.13 with Tkinter support. Either of these works:

- Homebrew:

  ```bash
  brew install python@3.12 python-tk@3.12
  ```

- Python.org installer:

  Download Python 3.12 or 3.13 from <https://www.python.org/downloads/macos/>.

Then from this project folder:

1. Create a virtual environment:

   ```bash
   python3.12 -m venv .venv
   ```

2. Activate it and install dependencies:

   ```bash
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install -e .
   ```

3. Run the app:

   ```bash
   python -m pdf_to_jpg_app
   ```

## Build a Mac app

Build on macOS:

```bash
./scripts/build-mac.sh
```

The app bundle will be created under `dist/`. Open it with:

```bash
open "dist/PDF to JPG Converter.app"
```

## Build a Windows exe

Build the Windows executable on Windows, in a Windows VM, or in Windows CI. PyInstaller does not cross-compile a Windows `.exe` from macOS.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
.\scripts\build-windows.ps1
```

The executable will be created under `dist\PDF to JPG Converter.exe`.

If Windows reports `No module named PyInstaller` or `No module named Pyinstaller`, reinstall dependencies inside the project venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
.\scripts\build-windows.ps1
```

Python module casing matters when running PyInstaller manually. Use:

```powershell
python -m PyInstaller
```

not `python -m Pyinstaller`.

The main launcher file is `pdf_to_jpg_converter.py`. A `pdf_to_jpg_convertor.py` alias is also included for the alternate spelling, but the build script uses `converter`.

If the built Windows app opens with `No module named 'pdf_to_jpg_app'`, `No module named 'pymupdf'`, or `No module named 'fitz'`, rebuild with the current `scripts\build-windows.ps1`. It passes the `src` folder and PyMuPDF collection flags to PyInstaller explicitly. Manual equivalent:

```powershell
python -m PyInstaller --name "PDF to JPG Converter" --windowed --onefile --clean --noconfirm --paths .\src --collect-all pymupdf --collect-all fitz --hidden-import pymupdf --hidden-import fitz --hidden-import pdf_to_jpg_app.gui --hidden-import pdf_to_jpg_app.converter .\pdf_to_jpg_converter.py
```

## Settings

- DPI controls rendered image resolution. `300` is a good default for scanned documents.
- JPEG quality controls file size and visual quality. `90` is a good default.
- Existing files are skipped by default. Enable overwrite if you want to replace them.

## Development checks

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```
