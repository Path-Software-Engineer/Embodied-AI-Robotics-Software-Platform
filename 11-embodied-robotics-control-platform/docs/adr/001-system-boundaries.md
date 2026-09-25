# ADR 001 — Fronteras y protocolos

Estado: aceptado para Sprint 1. Fecha: 2026-09-25.

## Decisión

React + React Three Fiber observa snapshots y eventos. FastAPI expone HTTP para consultas/configuración y WebSocket para telemetría/feedback. Un orchestrator separado expone gRPC tipado hacia el gateway y traduce a ROS 2. ROS contiene topics, services y actions; TimescaleDB recibe escritura asíncrona para trazas y replay.

## Motivo

Cada proceso tiene una responsabilidad distinta: render, borde autenticado, coordinación, transporte robótico y persistencia. El navegador no participa en control crítico. Los adapters hacen explícita la conversión de clocks, frames y tipos; el dominio no depende de HTTP ni de ROS.

## Consecuencias

Se requieren contratos protobuf/ROS/HTTP/WS versionados, health por proceso, correlation IDs y tests de integración. El sistema tiene más costo de arranque local; esa complejidad se acepta únicamente si el vertical real funciona en el gate.
