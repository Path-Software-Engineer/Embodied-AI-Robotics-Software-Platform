$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Run .\scripts\setup.ps1 first." }
if (-not $env:EMBODIED_OPERATOR_TOKEN -or $env:EMBODIED_OPERATOR_TOKEN.Length -lt 32) {
    $env:EMBODIED_OPERATOR_TOKEN = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
}
docker compose down --remove-orphans | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Could not stop previous local test stack." }
try {
    docker compose build web
    if ($LASTEXITCODE -ne 0) { throw "Control board web image build failed." }
    docker compose up --detach --wait --wait-timeout 240
    if ($LASTEXITCODE -ne 0) { throw "Control stack failed readiness." }
    docker compose exec -T sim bash -lc `
        'source /opt/ros/jazzy/setup.bash; source /workspace/ros_ws/install/setup.bash; python /workspace/scripts/smoke-action.py'
    if ($LASTEXITCODE -ne 0) { throw "Sprint 1 compatibility smoke failed." }
    & $Python scripts/smoke-control.py
    if ($LASTEXITCODE -ne 0) {
        docker compose logs --tail 100 gateway sim
        throw "Sprint 2 control smoke failed."
    }
    npm run e2e --prefix apps/web
    if ($LASTEXITCODE -ne 0) {
        docker compose logs --tail 100 gateway sim
        throw "Sprint 2 browser acceptance failed."
    }
}
finally {
    docker compose down --remove-orphans | Out-Null
}
