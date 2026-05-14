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

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
  Write-Host "Creating Windows virtual environment in .venv..."

  try {
    & py -3.12 -m venv ".venv"
    $VenvExitCode = $LASTEXITCODE
  } catch {
    $VenvExitCode = 1
  }

  if ($VenvExitCode -ne 0) {
    try {
      & python -m venv ".venv"
      $VenvExitCode = $LASTEXITCODE
    } catch {
      $VenvExitCode = 1
    }
  }

  if ($VenvExitCode -ne 0 -or -not (Test-Path $Python)) {
    Write-Host ""
    Write-Host "Could not create .venv."
    Write-Host "Install Python 3.12 for Windows, then run this script again."
    exit 1
  }
}

try {
  & $Python -m PyInstaller --version | Out-Null
  $PyInstallerExitCode = $LASTEXITCODE
} catch {
  $PyInstallerExitCode = 1
}

if ($PyInstallerExitCode -ne 0) {
  Write-Host "Installing PyInstaller and project dependencies into .venv..."
  & $Python -m pip install --upgrade pip
  & $Python -m pip install -r "requirements.txt"
  & $Python -m pip install -e "."
}

try {
  & $Python -c "import pymupdf, fitz; print('PyMuPDF import ok')"
  $PyMuPDFExitCode = $LASTEXITCODE
} catch {
  $PyMuPDFExitCode = 1
}

if ($PyMuPDFExitCode -ne 0) {
  Write-Host "Installing PyMuPDF into .venv..."
  & $Python -m pip install -r "requirements.txt"
  & $Python -m pip install -e "."
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
