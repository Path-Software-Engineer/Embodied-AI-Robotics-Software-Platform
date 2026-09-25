$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$Candidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
    "python"
)
$Python = $null
foreach ($Candidate in $Candidates) {
    try {
        & $Candidate -c "import sys; assert sys.version_info >= (3, 12)" 2>$null
        if ($LASTEXITCODE -eq 0) { $Python = $Candidate; break }
    }
    catch { continue }
}
if (-not $Python) { throw "Python 3.12+ is required." }

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    & $Python -m venv (Join-Path $Root ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Python virtual environment creation failed." }
}
& $VenvPython -m pip install -r services/requirements.txt -r services/requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

npm ci --prefix apps/web --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw "Web dependency installation failed." }
Write-Host "OK - Project 11 Sprint 1 dependencies installed"
