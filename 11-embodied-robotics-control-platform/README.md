# Embodied Robotics Control Platform

Proyecto 11 del Path Software Engineer. La plataforma observará un robot **simulado** mediante Gazebo Sim y ROS 2, y presentará su estado, el ciclo de agente y la evidencia temporal en una interfaz React. No controla hardware físico ni afirma seguridad certificada.

## Estado

Sprint 1 — Embodied Agent Loop Visualizer. El gate local ejecuta la simulación real, la acción ROS, la persistencia, el replay y las pruebas de navegador antes de publicar la etiqueta `v0.1.0-sprint-01-embodied-agent-loop-visualizer`. El mapa vigente está adjunto a la tarea que inició este trabajo; [plan.md](docs/sprint-01/plan.md) traduce ese alcance a entregables verificables.

El [brief original del proyecto](docs/original-project-brief.md) se conserva íntegro como referencia del roadmap; este README describe el entregable ejecutable del Sprint 1.

## Fronteras

```text
Gazebo Sim → ROS 2 → orchestrator/gRPC → FastAPI/WebSocket → React/R3F
                        ↓                         ↓
                 safety authorization       TimescaleDB
```

- El navegador observa y solicita; no publica en ROS.
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

## Reproducir localmente

```powershell
Set-Location "C:\JeanLoa\Path-Software-Engineer\Embodied-AI-Robotics-Software-Platform\11-embodied-robotics-control-platform"
.\scripts\setup.ps1
.\scripts\run-quality-gate.ps1
```

Para abrir la aplicación después del gate, ejecutar `docker compose up --detach --wait --wait-timeout 240` y visitar `http://127.0.0.1:3000`; Swagger está en `http://127.0.0.1:8000/docs`. El gateway expone solo lectura: la acción simulada de aceptación se invoca por ROS desde el contenedor, no desde un endpoint público. El replay permite elegir runs persistidos y no modifica el run vivo.

Los repositorios de AI Engineer y Software Engineer permanecen separados. Un bundle externo debe pasar validación de esquema, hash y procedencia antes de ser aceptado; nunca ejecutamos código importado.
