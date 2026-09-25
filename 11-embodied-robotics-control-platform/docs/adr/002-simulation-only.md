# ADR 002 — Gazebo y simulación solamente

Estado: aceptado para v1.0.0. Fecha: 2026-09-25.

## Decisión

Gazebo Sim Harmonic con ROS 2 Jazzy es la única fuente de pose y feedback de producción de la release planificada. Robot, world, physics, seed, clocks y escenario son manifests versionados. No hay adaptador a hardware físico.

## Motivo

Permite trazas reproducibles y fault injection acotado. La simulación no permite afirmar seguridad ni rendimiento de un robot real.

## Consecuencias

Toda pantalla debe indicar simulación o replay. Los assets llevan hash/licencia y los runs identifican versión del simulador. Incorporar hardware requiere otra release, hazard analysis, drivers, límites y autorización explícita.
