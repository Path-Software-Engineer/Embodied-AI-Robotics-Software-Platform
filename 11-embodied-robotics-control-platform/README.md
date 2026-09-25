# Embodied Robotics Control Platform

Proyecto 11 del Path Software Engineer. La plataforma observa y controla de forma supervisada un robot **simulado** mediante Gazebo Sim y ROS 2, y presenta estado, planificación y evidencia temporal en React. No controla hardware físico ni afirma seguridad certificada.

## Estado

Sprint 1 — Embodied Agent Loop Visualizer — quedó etiquetado como `v0.1.0-sprint-01-embodied-agent-loop-visualizer`. El Sprint 2 añade un control board local con lease exclusiva, plan ligado al snapshot, aprobación explícita, ROS Action y supervisor C++ independiente. El gate ejecuta ambos flujos y las pruebas de navegador antes de permitir un cierre del Sprint 2.

El [brief original del proyecto](docs/original-project-brief.md) se conserva íntegro como referencia del roadmap. Los límites del control path están en [control-path.md](docs/sprint-02/control-path.md) y la evidencia de riesgos en [safety-case.md](docs/sprint-02/safety-case.md).

## Fronteras

```text
Gazebo Sim → ROS 2 → orchestrator/gRPC → FastAPI/WebSocket → React/R3F
                        ↓                         ↓
                 safety authorization       TimescaleDB
```

- El navegador observa y solicita bajo un token local; no publica en ROS.
- El supervisor de seguridad autoriza cualquier movimiento simulado. El planner no puede omitirlo.
- TimescaleDB almacena evidencia, sin participar en decisiones de seguridad.
- Replay es solo lectura y nunca apunta a un run vivo.
- Cada muestra tiene `run_id`, `frame_id`, unidad, reloj, timestamp, secuencia y procedencia.

## Documentos de inicio

- [Exploración del Día 1695](docs/sprint-01/exploration.md)
- [Plan y criterios de cierre](docs/sprint-01/plan.md)
- [Compatibilidad y presupuestos](docs/sprint-01/compatibility.md)
- [ADR 001: fronteras y protocolos](docs/adr/001-system-boundaries.md)
- [ADR 002: simulación](docs/adr/002-simulation-only.md)
- [ADR 003: autoridad y seguridad](docs/adr/003-safety-authority.md)
- [Runbook de ejecución y verificación](docs/sprint-01/runbook.md)
- [Revisión de cierre y límites](docs/sprint-01/review.md)
- [Control path y contratos del Sprint 2](docs/sprint-02/control-path.md)
- [Safety case del Sprint 2](docs/sprint-02/safety-case.md)
- [Runbook del Sprint 2](docs/sprint-02/runbook.md)
- [Revisión del Sprint 2 y límites de release](docs/sprint-02/review.md)

## Reproducir localmente

```powershell
Set-Location "C:\JeanLoa\Path-Software-Engineer\Embodied-AI-Robotics-Software-Platform\11-embodied-robotics-control-platform"
.\scripts\setup.ps1
.\scripts\run-quality-gate.ps1
```

Para abrir la aplicación después del gate, crear `EMBODIED_OPERATOR_TOKEN` en el PowerShell actual antes de `docker compose up --detach --wait --wait-timeout 240` y visitar `http://127.0.0.1:3000`; Swagger está en `http://127.0.0.1:8000/docs`. [El runbook del Sprint 2](docs/sprint-02/runbook.md) contiene los comandos. La API `/api/v2` acepta comandos autenticados solo para el simulador local; el replay permite elegir runs persistidos y no modifica el run vivo.

Los repositorios de AI Engineer y Software Engineer permanecen separados. Un bundle externo debe pasar validación de esquema, hash y procedencia antes de ser aceptado; nunca ejecutamos código importado.
