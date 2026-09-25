# Día 1695 — Exploración del producto

## Evidencia de entrada

- Proyecto 10 de Software Engineer: tag local `v0.3.0-sprint-03-developer-api-docs-builder` en commit `3d0110a`; repositorio limpio en `main`. El despliegue Azure posterior está bloqueado por la suscripción deshabilitada y no se considera parte de esta precondición de cierre local.
- Proyecto 60 de AI Engineer: tag local `v1.0.0-quantum-first-platform-roadmap` en commit `6f83e45`; repositorio limpio en `main`. Su bundle es `technical_candidate_unapproved` y tiene `approval: null`. No se usará como autorización para lanzar el Proyecto 61 ni como fuente de acciones robóticas.
- Proyecto 11: checkout propio `Embodied-AI-Robotics-Software-Platform`, base `main` limpia en `7fb966d`. Trabajo iniciado en `feature/s1-d1695-embodied-robotics-exploration`.

Estos son hechos locales observados el 25-09-2026; no demuestran estado remoto ni aprobación externa.

## Personas y escenarios

| Persona | Necesidad | Escenario inicial | Evidencia esperada |
| --- | --- | --- | --- |
| Operador de simulación | Saber si el estado es actual y qué acción ocurrió | Ejecuta un escenario acotado, ve pose, feedback y alarmas | Snapshot con reloj, frame, secuencia, fuente y eventos correlacionados |
| Desarrollador de integración | Diagnosticar pérdida de datos o desacuerdo entre sistemas | Inspecciona ROS, gRPC, gateway y DB | Trazas con `correlation_id`, gaps y razón de rechazo |
| Revisor técnico | Verificar arquitectura y límites | Reproduce un run sin control sobre la simulación viva | Manifests, hashes, golden trace y pruebas de aislamiento |
| Reclutador | Entender el sistema sin instalar ROS | Revisa una demo grabada y el README | Evidencia reproducible, etiquetas simulation/replay y límites claros |

## Historias de usuario

1. Como operador quiero ver pose y articulaciones con edad de muestra para no confundir datos viejos con estado actual.
2. Como operador quiero distinguir estado live, replay, degradado y desconectado sin depender solo del color.
3. Como desarrollador quiero seguir un `correlation_id` desde una intención hasta el feedback de ROS.
4. Como revisor quiero repetir un escenario desde robot/world/seed/versiones y comparar la traza resultante.
5. Como revisor quiero comprobar que replay y una conexión WebSocket no pueden mandar comandos al robot.

## Historias técnicas y atributos

| Historia | Atributo medible inicial |
| --- | --- |
| Contratos versionados ROS, protobuf, HTTP y WS | Un cambio incompatible rompe un test de fixture; campos desconocidos no cambian semántica silenciosamente |
| Estado inmutable con clocks y frames | Toda muestra tiene reloj y frame explícitos; secuencia creciente por fuente |
| Transporte desacoplado | Caída de DB o web no altera autorización de seguridad ni ejecución ROS |
| Backpressure visual | Cola por cliente acotada; gaps visibles; snapshot completo tras reconectar |
| Replay aislado | Una sesión de replay no posee canal de comandos ni control lease |
| Accesibilidad | Tabla equivalente a escena 3D; teclado y reduced motion; estado textual |

## Riesgos y amenazas iniciales

| Riesgo | Control propuesto | Prueba requerida |
| --- | --- | --- |
| Estado stale presentado como actual | Freshness threshold y overlay textual | Cortar stream y verificar degradación |
| Frame o unidad equivocada | SI, frame tree versionado y validación en el borde | Fixture con frame incompatible rechazado |
| Secuencia duplicada o reordenada | Secuencia monotónica por fuente/lease | Duplicado rechazado sin ejecución |
| Planner salta seguridad | Supervisor en proceso separado y autorización obligatoria | Planner/gateway falsos no ejecutan sin supervisor |
| Replay actúa sobre run vivo | Puerto/API de replay solo lectura e IDs separados | Test de ausencia de side effects |
| Bundle no confiable | Schema, tamaño, hash, allowlist y sin ejecución de código | Manifest alterado rechazado |
| Pérdida de heartbeat | Watchdog y safe state | Fault test con corte de heartbeat |
| Persistencia bloquea control | Writer en proceso/cola separados | DB apagada durante la misión |

## Alcance

Sprint 1 implementa el visualizador del ciclo embodied sobre simulación. No incluye planificación multi-paso, modos/leases completos ni tarjetas de arquitectura de Sprints 2 y 3. No se conecta hardware, no se importan modelos o notebooks de AI Engineer y no se despliega infraestructura final durante la exploración.

## Preguntas de investigación pendientes

- Medir en Docker Desktop el tiempo real de arranque de Gazebo headless y el costo de memoria del stack.
- Fijar digest de imágenes y versiones exactas de dependencias al crear el build reproducible.
- Confirmar los topics del modelo SDF y QoS del bridge con una ejecución real antes de congelar los contratos.
