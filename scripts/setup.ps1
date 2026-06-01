# English Learning Agent — Local setup script
# Run: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host "=== English Learning Agent Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create virtual environment
$VenDir = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenDir)) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenDir
    Write-Host "      Created at: $VenDir" -ForegroundColor Green
} else {
    Write-Host "[1/4] Virtual environment already exists at $VenDir" -ForegroundColor Green
}

# Step 2: Activate and upgrade pip
$Pip = Join-Path $VenDir "Scripts\pip.exe"
$Python = Join-Path $VenDir "Scripts\python.exe"

Write-Host "[2/4] Upgrading pip..." -ForegroundColor Yellow
& $Pip install --upgrade pip

# Step 3: Install requirements (editable mode)
Write-Host "[3/4] Installing Python dependencies (editable)..." -ForegroundColor Yellow
& $Pip install -e $ProjectRoot

# Step 4: Download spaCy model
Write-Host "[4/4] Downloading spaCy English model..." -ForegroundColor Yellow
& $Python -m spacy download en_core_web_sm

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment, run:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run the tool:" -ForegroundColor White
Write-Host "  python src/main.py --video samples\example.mp4" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run tests:" -ForegroundColor White
Write-Host "  python -m pytest tests\ -v" -ForegroundColor Yellow
