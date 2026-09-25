# Sprint 1 runbook — simulation only

## Prerequisites

- Windows PowerShell, Docker Desktop Linux engine, Node 24+, Python 3.12+ y Chrome para Playwright.
- Espacio suficiente para la imagen ROS 2/Gazebo. Los puertos 3000 y 8000 deben estar libres.
- No requiere Azure, credenciales, hardware ni bundles de AI Engineer.

## Bootstrap y quality gate

```powershell
Set-Location "C:\JeanLoa\Path-Software-Engineer\Embodied-AI-Robotics-Software-Platform\11-embodied-robotics-control-platform"
.\scripts\setup.ps1
.\scripts\run-quality-gate.ps1
```

El gate construye las imágenes, verifica Python/TypeScript/ROS/GTest/URDF, inicia los cuatro servicios, ejecuta un goal ROS Action real, verifica autorización, feedback, persistencia, replay y Playwright, y detiene los contenedores en `finally`. Conserva el volumen TimescaleDB; `docker compose down --volumes` borraría esa evidencia y **no** forma parte del gate.

## Inspección manual

```powershell
docker compose up --detach --wait --wait-timeout 240
Start-Process "http://127.0.0.1:3000"
Start-Process "http://127.0.0.1:8000/docs"
```

La web está en `http://127.0.0.1:3000`, la API en `http://127.0.0.1:8000`, Swagger en `/docs` y OpenAPI en `/openapi.json`. La web es un observador sin controles de movimiento. El escenario de aceptación se ejecuta solo dentro del contenedor sim:

```powershell
docker compose exec -T sim bash -lc 'source /opt/ros/jazzy/setup.bash; source /workspace/ros_ws/install/setup.bash; python /workspace/scripts/smoke-action.py'
```

Luego consultar:

```powershell
$State = Invoke-RestMethod "http://127.0.0.1:8000/api/v1/robots/embodied_demo/state"
$RunId = $State.state.run_id
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/simulation-runs/$RunId/loop-events?limit=30"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/simulation-runs/$RunId/samples?limit=10"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/simulation-runs?limit=20"
```

Para detener sin eliminar las muestras:

```powershell
docker compose down --remove-orphans
```

## Failures y límites

- `DISCONNECTED`: comprobar `docker compose ps` y `docker compose logs gateway sim`. La API requiere el paquete `websockets` para el upgrade; el gate de navegador detecta su ausencia.
- `STALE DATA`: un frame con más de 1 s de edad no se considera actual.
- `DEGRADED TELEMETRY`: DB no disponible o hubo muestras descartadas por backpressure. El supervisor ROS no depende de la DB.
- Action abortada: inspeccionar `/simulation/authorize_motion`, feedback ROS y `docker compose logs sim`. Un target fuera de ±0.8 rad o secuencia repetida se rechaza.
- Replay obtiene snapshots/eventos persistidos por HTTP y nunca publica en ROS. Sigue siendo evidencia de simulación, no un ensayo en hardware.
- Cada arranque genera un `run_id` distinto para que el replay no mezcle muestras de ejecuciones anteriores conservadas en el volumen.
- `robot.urdf.xacro` es el contrato cinemático ROS; `model.sdf` es el activo que Gazebo ejecuta. Ambos se verifican por hash. La física depende de Gazebo/CPU; se exige tolerancia angular, no una traza numérica idéntica bit a bit.
