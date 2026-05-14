$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
$Launcher = Join-Path $ProjectRoot "pdf_to_jpg_converter.py"

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

& $Python -m PyInstaller `
  --name "PDF to JPG Converter" `
  --windowed `
  --onefile `
  --clean `
  --noconfirm `
  "$Launcher"

Write-Host "Built dist\PDF to JPG Converter.exe"
