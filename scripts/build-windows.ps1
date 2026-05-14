$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
$Launcher = Join-Path $ProjectRoot "pdf_to_jpg_converter.py"
$SourceDir = Join-Path $ProjectRoot "src"
$PackageDir = Join-Path $SourceDir "pdf_to_jpg_app"

if (-not (Test-Path $Launcher)) {
  Write-Host ""
  Write-Host "Could not find pdf_to_jpg_converter.py."
  Write-Host "This file should be in the project root folder:"
  Write-Host "  $ProjectRoot"
  Write-Host ""
  Write-Host "Make sure you copied the whole project folder, including:"
  Write-Host "  pdf_to_jpg_converter.py"
  Write-Host "  pyproject.toml"
  Write-Host "  requirements.txt"
  Write-Host "  src\pdf_to_jpg_app\"
  exit 1
}

if (-not (Test-Path $PackageDir)) {
  Write-Host ""
  Write-Host "Could not find the pdf_to_jpg_app package."
  Write-Host "This folder should exist:"
  Write-Host "  $PackageDir"
  Write-Host ""
  Write-Host "Make sure you copied the whole project folder, including src\pdf_to_jpg_app\."
  exit 1
}

$Python = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
  $Python = "python"
}

try {
  & $Python -m PyInstaller --version | Out-Null
  $PyInstallerExitCode = $LASTEXITCODE
} catch {
  $PyInstallerExitCode = 1
}

if ($PyInstallerExitCode -ne 0) {
  Write-Host ""
  Write-Host "PyInstaller is not installed for this Python environment."
  Write-Host "From the project folder, run:"
  Write-Host "  py -3.12 -m venv .venv"
  Write-Host "  .\.venv\Scripts\Activate.ps1"
  Write-Host "  python -m pip install --upgrade pip"
  Write-Host "  python -m pip install -r requirements.txt"
  Write-Host "  python -m pip install -e ."
  Write-Host ""
  Write-Host "If running manually, use 'PyInstaller' with a capital I: python -m PyInstaller"
  exit 1
}

try {
  & $Python -c "import pymupdf, fitz; print('PyMuPDF import ok')"
  $PyMuPDFExitCode = $LASTEXITCODE
} catch {
  $PyMuPDFExitCode = 1
}

if ($PyMuPDFExitCode -ne 0) {
  Write-Host ""
  Write-Host "PyMuPDF is not installed for this Python environment."
  Write-Host "Install dependencies in the same venv used for building:"
  Write-Host "  .\.venv\Scripts\Activate.ps1"
  Write-Host "  python -m pip install -r requirements.txt"
  Write-Host "  python -m pip install -e ."
  exit 1
}

& $Python -m PyInstaller `
  --name "PDF to JPG Converter" `
  --windowed `
  --onefile `
  --clean `
  --noconfirm `
  --paths "$SourceDir" `
  --collect-all "pymupdf" `
  --collect-all "fitz" `
  --hidden-import "pymupdf" `
  --hidden-import "fitz" `
  --hidden-import "pdf_to_jpg_app.gui" `
  --hidden-import "pdf_to_jpg_app.converter" `
  "$Launcher"

Write-Host "Built dist\PDF to JPG Converter.exe"
