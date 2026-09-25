# Sprint 1 changelog

## Added

- Gazebo Sim headless con world y robot articulado originales, semilla y manifiesto SHA-256.
- Bridge ROS 2 Jazzy de reloj, pose y comando de hombro; protobuf gRPC de estado y eventos.
- ROS Action `MoveJoint` y supervisor C++ separado que rechaza alcance, límite o secuencia inválida.
- Gateway FastAPI de observación, WebSockets, persistencia TimescaleDB, catálogo de runs y replay de solo lectura.
- Digital twin React Three Fiber alimentado por poses de Gazebo, tabla alternativa, estados de frescura y ciclo correlacionado. El replay permite seleccionar un run persistido, navegar muestras y variar la velocidad de reproducción sin modificar ROS.
- Gate local: Python, web, ROS, GoogleTest, URDF, Gazebo/Action, persistencia, Chrome Playwright y axe.

## Boundaries

- Solo simulación local. No se conectaron dispositivos físicos, cloud, modelos externos ni comandos desde el navegador.
- El supervisor es un control demostrativo de límites para un único escenario, no un sistema de seguridad certificado ni la implementación completa de modos/leases de Sprint 2.
