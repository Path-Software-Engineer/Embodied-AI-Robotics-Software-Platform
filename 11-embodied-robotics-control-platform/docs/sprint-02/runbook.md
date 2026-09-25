# Sprint 2 local runbook

From a regular PowerShell window with Docker Desktop running:

```powershell
Set-Location "C:\JeanLoa\Path-Software-Engineer\Embodied-AI-Robotics-Software-Platform\11-embodied-robotics-control-platform"
.\scripts\setup.ps1
.\scripts\run-quality-gate.ps1
```

The gate generates a process-local random operator token if one is absent, starts a disposable Compose stack, runs Python/TypeScript/C++ checks, the Sprint 1 action compatibility smoke, the Sprint 2 HTTP control, terminal cancellation and active-action EStop fault smokes, local API latency samples, and six browser flows, then stops containers. It **does not delete** the TimescaleDB volume. Do not paste a token into chat or commit one.

For an interactive demo, generate your own token before `docker compose up` in the same PowerShell process:

```powershell
$env:EMBODIED_OPERATOR_TOKEN = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
docker compose up --detach --wait --wait-timeout 240
```

Open `http://127.0.0.1:3000`; API docs are at `http://127.0.0.1:8000/docs`. The token is entered in the control board and retained only in tab memory. Obtain a lease, confirm Manual mode, propose a target within ±0.8 rad, review its snapshot, approve, execute, and inspect ROS feedback and audit. Replay is read-only. Stop locally with `docker compose down --remove-orphans` (no `--volumes`).

If a check fails, diagnose the first substantive error above the final PowerShell `throw`. `scripts/run-control-smoke.ps1` is the focused cross-layer rerun. A disabled Azure subscription is not relevant to this local sprint and must not be bypassed by deployment.
