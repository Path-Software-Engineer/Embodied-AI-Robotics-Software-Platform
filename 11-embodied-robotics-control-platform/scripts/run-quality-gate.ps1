$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Command)
    Write-Host "  -> $Label"
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
}

if (-not (Test-Path $Python) -or -not (Test-Path "apps/web/node_modules")) {
    throw "Run .\scripts\setup.ps1 before this quality gate."
}
if (-not $env:EMBODIED_OPERATOR_TOKEN -or $env:EMBODIED_OPERATOR_TOKEN.Length -lt 32) {
    $env:EMBODIED_OPERATOR_TOKEN = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
}

Write-Host "[1/5] Static contracts and code"
$env:PYTHONPATH = "$Root;$Root\services\generated"
Invoke-Checked "Ruff lint" { & $Python -m ruff check services tests scripts --force-exclude }
Invoke-Checked "Ruff format" { & $Python -m ruff format --check services tests scripts --force-exclude }
Invoke-Checked "Python tests" { & $Python -m pytest -q }
Invoke-Checked "Web TypeScript and production build" { npm run build --prefix apps/web }
Invoke-Checked "Web tests" { npm run test --prefix apps/web }
Invoke-Checked "Docker Compose model" { docker compose config --quiet }

Write-Host "[2/5] Building pinned ROS/Gazebo and web images"
Invoke-Checked "Container images" { docker compose build sim web }

Write-Host "[3/5] Starting real simulator and database"
docker compose down --remove-orphans | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Previous test stack could not stop cleanly." }
try {
    Invoke-Checked "Healthy cross-layer platform" {
        docker compose up --detach --wait --wait-timeout 240
    }
    Invoke-Checked "URDF/Xacro validity" {
        docker compose exec -T sim bash -lc `
            'source /opt/ros/jazzy/setup.bash; xacro /workspace/sim/models/embodied_demo/robot.urdf.xacro > /tmp/embodied_demo.urdf && check_urdf /tmp/embodied_demo.urdf'
    }
    Invoke-Checked "C++ safety supervisor GoogleTest" {
        docker compose exec -T sim bash -lc `
            'source /opt/ros/jazzy/setup.bash; source /workspace/ros_ws/install/setup.bash; cd /workspace/ros_ws; colcon test --packages-select safety_supervisor --event-handlers console_cohesion+ && colcon test-result --verbose'
    }
    Write-Host "[4/5] Running real Gazebo/ROS Action and control-board acceptance"
    Invoke-Checked "Action, safety, loop, persistence and replay smoke" {
        docker compose exec -T sim bash -lc `
            'source /opt/ros/jazzy/setup.bash; source /workspace/ros_ws/install/setup.bash; python /workspace/scripts/smoke-action.py'
    }
    Invoke-Checked "Exclusive lease, plan, approval, real action and EStop smoke" {
        & $Python scripts/smoke-control.py
    }
    Invoke-Checked "Local read and plan-persistence latency smoke" {
        & $Python scripts/benchmark-control.py
    }
    Invoke-Checked "Chrome control board, replay, accessibility and mobile E2E" {
        npm run e2e --prefix apps/web
    }
    Write-Host "[5/5] Repository hygiene"
    Invoke-Checked "Git whitespace" { git diff --check }
    Invoke-Checked "Staged Git whitespace" { git diff --cached --check }
    Write-Host "OK - Project 11 Sprint 2 core quality gate passed (see docs/sprint-02/review.md)"
}
finally {
    docker compose down --remove-orphans | Out-Null
}
