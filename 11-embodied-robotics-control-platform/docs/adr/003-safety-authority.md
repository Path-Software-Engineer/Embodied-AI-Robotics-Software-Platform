# ADR 003 — Autoridad de seguridad

Estado: aceptado como frontera arquitectónica; implementación del supervisor independiente en etapas posteriores. Fecha: 2026-09-25.

## Decisión

Un planner puede proponer acciones, pero toda acción ejecutable debe ser autorizada por un supervisor C++ independiente. El gateway valida actor, modo, lease, robot/run, versión esperada y secuencia antes de enviar una solicitud. El supervisor vuelve a validar límites y heartbeat sin depender de UI o DB.

Stop, cancel y simulated EStop tienen transiciones y APIs diferentes. EStop es latched; no se borra por reconexión. Replay no tiene canal de comandos. Falta de supervisor significa rechazo, nunca autorización implícita.

## Consecuencias

Se necesita probar duplicados, staleness, modo erróneo, heartbeat perdido y fallos de gateway/DB. En el Sprint 1 no se mostrará ningún botón de movimiento como operativo hasta comprobar la autorización y el ROS Action real. El futuro supervisor no convierte el sistema en equipo de seguridad certificado.
