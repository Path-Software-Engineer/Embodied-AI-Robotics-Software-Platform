# Compatibilidad y presupuestos iniciales

Consultado el 25-09-2026. Versión elegida como baseline: Ubuntu 24.04 Noble, ROS 2 Jazzy y Gazebo Harmonic. La [matriz oficial de Gazebo](https://gazebosim.org/docs/garden/ros_installation/) los marca como combinación recomendada. [ROS Jazzy soporta Noble](https://docs.ros.org/en/jazzy/Installation/Alternatives/Ubuntu-Install-Binary.html) y [Gazebo Harmonic publica binarios para Noble](https://gazebosim.org/docs/harmonic/install_ubuntu/). El [bridge ros_gz](https://gazebosim.org/docs/harmonic/ros2_integration/) requiere verificar los tipos concretos antes de usarlos.

| Componente | Selección inicial | Razón | Pendiente de fijar |
| --- | --- | --- | --- |
| Base ROS | `ros:jazzy-ros-base-noble` | Imagen oficial para Noble | Digest amd64 tras pull y build |
| Simulador | Gazebo Harmonic | LTS recomendado con Jazzy | Paquetes y versión exacta en imagen |
| Python | 3.12 en Noble | Runtime compatible con Jazzy | Lock transitive para gateway |
| Node | 24 | LTS instalado localmente | Tag/digest y lock npm |
| PostgreSQL/Timescale | PostgreSQL 17 + TimescaleDB | Misma familia ya utilizada por proyectos previos | Digest, extensión, política de retention |
| C++ | C++17 | ROS Jazzy y soporte de toolchain | Compilador/flags del contenedor |

No se declara compatibilidad de interfaces concretas ni performance hasta ejecutar el stack. La exploración no congela versiones de librerías React/Python.

## Hipótesis de presupuesto, sujetas a medición

| Métrica | Objetivo inicial | Cómo medir |
| --- | --- | --- |
| Edad de pose visible | ≤ 500 ms en local; stale a > 1 s | Timestamp de simulación y wall clock mostrados por separado |
| Telemetría al navegador | 10 Hz máximo por cliente | Contadores de entrega/gap en gateway |
| Primer snapshot tras reconexión | ≤ 2 s tras restablecer transporte | Prueba con desconexión deliberada |
| Latencia de acción simulada | Percentiles documentados, sin promesa de hardware | Trace desde intención hasta feedback ROS |
| Memoria del stack | Medir pico y steady state en Docker Desktop | `docker stats` durante escenario headless |
| UI | 30 FPS objetivo en equipo de desarrollo; tabla funcional sin WebGL | Perfil de navegador y prueba fallback |

Ninguna cifra anterior es evidencia de rendimiento; son umbrales de diseño para evaluar cuando exista implementación.
