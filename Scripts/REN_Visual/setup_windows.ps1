$ErrorActionPreference = "Stop"

Write-Host "REN Visual Factory setup" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not available on PATH."
}

python -m pip install -r Scripts/REN_Visual/requirements.txt

Write-Host ""
Write-Host "Python dependencies installed." -ForegroundColor Green

if ($env:OPENAI_API_KEY) {
    Write-Host "OPENAI_API_KEY is available in this shell." -ForegroundColor Green
} else {
    Write-Host "OPENAI_API_KEY is NOT set in this shell." -ForegroundColor Yellow
    Write-Host "Set it locally as an environment variable. Do not paste it into chat or commit it."
}

python Scripts/REN_Visual/ren_visual.py audit
