# Sprint 1 — Embodied Agent Loop Visualizer

Ventana del mapa: días globales 1695–1722, 28 días activos. El Día 1695 es exploración. Los días siguientes son hitos de alcance, no afirmaciones de tiempo transcurrido; la aceptación depende del gate y de la revisión de cierre.

## Resultado verificable

Un escenario Gazebo headless mueve un robot simulado. ROS 2 publica el estado oficial; el orchestrator lo entrega por gRPC al gateway; el gateway persiste muestras en TimescaleDB y las emite por WebSocket. React Three Fiber dibuja la pose derivada de ese estado, junto con reloj, frame, edad de muestra y tabla alternativa. Un run terminado puede reconstruirse sin comandos.

## Secuencia de entrega

1. **Días 1695–1701:** investigación, contratos, workspace, Gazebo/ROS, DB y primera pose trazable.
2. **Días 1702–1708:** escena 3D, joints, objetos, stream acotado, timeline y replay solo lectura.
3. **Días 1709–1715:** percepción, snapshot, memoria acotada, intención no ejecutable, ROS Action simulado y grafo del loop.
4. **Días 1716–1722:** escenarios, trazas, freshness, pruebas integrales, documentación y release.

## Gate de Sprint 1

- Gazebo, ROS 2, orchestrator/gRPC, gateway, TimescaleDB y web levantan juntos y exponen health/readiness.
- Un test headless comprueba la procedencia de la pose desde Gazebo/ROS; la UI no usa poses o métricas de muestra en producción.
- Contratos y fixtures comprueban `run_id`, `robot_id`, `frame_id`, clock, unidad, timestamp, secuencia, source y schema_version.
- El loop percepción→estado→memoria→intención→acción→feedback conserva latencia, estado terminal y correlación.
- Replay no posee endpoint de escritura y un test comprueba que no afecta al run vivo.
- WebGL tiene alternativa 2D/tabular; estados stale, disconnected, degraded y unsafe son legibles sin color.
- Tests unitarios, de contrato, integración ROS/Gazebo, DB, Playwright y accesibilidad pasan; manifests y assets verifican hashes.
- README, ADRs, runbook, revisión y changelog están completos. Solo entonces se crea `v0.1.0-sprint-01-embodied-agent-loop-visualizer` y se integra Gitflow.

## Dependencias entre repositorios

El Sprint 1 corresponde conceptualmente al Proyecto 61 de AI Engineer. El bundle final de P60 tiene `approval: null`; ninguna salida de P61 se presupone disponible ni se incorpora hasta que exista y pase validación. La plataforma debe funcionar con un escenario propio de simulación, sin datos inventados.

## Fuera de alcance

Control de hardware, certificación de seguridad, planner de múltiples pasos, AutonomousSim completo, edge deployment y arquitectura Android. Estos requieren sprints o releases posteriores.
