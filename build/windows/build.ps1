#Requires -Version 5.1
<#
.SYNOPSIS
    Builds the Markforge Windows installer locally.
.DESCRIPTION
    Generates markforge.ico, runs PyInstaller, then builds the Inno Setup installer.
    Run from the project root or from the build\windows directory.
.EXAMPLE
    cd build\windows
    .\build.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Resolve project root (two levels up when run from build\windows)
# ---------------------------------------------------------------------------
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir '..\..')).Path
Set-Location $ProjectRoot

Write-Host "==> Project root: $ProjectRoot" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
$missing = @()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $missing += "Python  – install from https://python.org"
}

$magickCmd = Get-Command magick -ErrorAction SilentlyContinue
if (-not $magickCmd) {
    $missing += "ImageMagick  – install from https://imagemagick.org/script/download.php#windows"
}

$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $isccPath)) {
    $isccPath = "C:\Program Files\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $isccPath)) {
    $missing += "Inno Setup 6  – install via 'choco install innosetup' or https://jrsoftware.org/isdl.php"
}

if ($missing.Count -gt 0) {
    Write-Host "`nThe following prerequisites are missing:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

# ---------------------------------------------------------------------------
# Step 1 – Generate ICO
# ---------------------------------------------------------------------------
Write-Host "`n==> Generating assets\markforge.ico ..." -ForegroundColor Cyan
& magick assets\markforge.svg `
    -define icon:auto-resize=256,128,64,48,32,16 `
    assets\markforge.ico
if ($LASTEXITCODE -ne 0) { Write-Error "ImageMagick failed"; exit 1 }

# ---------------------------------------------------------------------------
# Step 2 – Install / verify Python packages
# ---------------------------------------------------------------------------
Write-Host "`n==> Installing Python dependencies ..." -ForegroundColor Cyan
python -m pip install --quiet -r requirements.txt pyinstaller
if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed"; exit 1 }

# ---------------------------------------------------------------------------
# Step 3 – Run PyInstaller
# ---------------------------------------------------------------------------
Write-Host "`n==> Running PyInstaller ..." -ForegroundColor Cyan
python -m PyInstaller markforge.spec --clean
if ($LASTEXITCODE -ne 0) { Write-Error "PyInstaller failed"; exit 1 }

# ---------------------------------------------------------------------------
# Step 4 – Build Inno Setup installer
# ---------------------------------------------------------------------------
Write-Host "`n==> Building installer with Inno Setup ..." -ForegroundColor Cyan
& $isccPath "build\windows\markforge.iss"
if ($LASTEXITCODE -ne 0) { Write-Error "Inno Setup failed"; exit 1 }

$output = Join-Path $ProjectRoot "build\windows\Output\Markforge-Setup.exe"
if (Test-Path $output) {
    Write-Host "`n==> Done! Installer: $output" -ForegroundColor Green
} else {
    Write-Error "Installer not found at expected path: $output"
    exit 1
}
