# Building Projects Roadmap — Plan 11

## 🧠 Embodied AI & Robotics Concepts

Esta organización reúne los proyectos del **Plan 11 — Embodied AI & Robotics Concepts** dentro de **Building Projects**.

Este plan acompaña directamente al:

```txt id="bp11-ai-relation"
AI Engineer Plan 11 — Embodied AI, Humanoid Robotics & Android Systems
```

La idea central es construir visualizadores, tableros conceptuales, tarjetas de arquitectura y portales ligeros para explicar sistemas de Embodied AI, planificación robótica, control, humanoides y arquitectura de androides.

Mientras AI Engineer profundiza en percepción, memoria, acción, control, planificación, seguridad, human-robot interaction, humanoid robotics y android systems, Building Projects convierte una parte de ese aprendizaje en evidencia visual y comunicable.

```txt id="bp11-core"
entorno
→ percepción
→ memoria
→ decisión
→ planificación
→ control
→ seguridad
→ arquitectura visual
→ README claro
```

Building Projects no reemplaza los proyectos profundos de AI Engineer.

Los acompaña con herramientas pequeñas que permitan explicar sistemas encarnados de forma seria, visual y responsable.

---

# 🎯 Objetivo general

Construir herramientas visuales de Embodied AI y robótica capaces de:

* Explicar el ciclo observación → memoria → acción.
* Visualizar consecuencias de acciones en un entorno.
* Mostrar planificación de tareas robóticas.
* Diferenciar planner y controller.
* Explicar feedback loop y corrección de errores.
* Crear tarjetas de arquitectura humanoide.
* Mostrar sensores, actuadores, percepción, memoria, control y safety.
* Comunicar android systems como arquitectura seria, no fantasía.
* Crear evidencia visual para GitHub.
* Acompañar la ruta principal sin inflar el alcance.

---

# 🔗 Regla de match del Plan 11

Building Projects hará match solo con los proyectos impares de AI Engineer.

```txt id="bp11-match-rule"
Proyecto 61 IA → Proyecto 31 Building
Proyecto 62 IA → Nada
Proyecto 63 IA → Proyecto 32 Building
Proyecto 64 IA → Nada
Proyecto 65 IA → Proyecto 33 Building
Proyecto 66 IA → Nada
```

Esto significa que este plan tendrá **3 proyectos**, no 6.

Cada proyecto Building toma como referencia la duración del proyecto IA correspondiente.

---

# 🗺️ Cronograma Plan 11

| Semana Building |                      Proyecto Building | Match IA |  Duración | Objetivo                                                                |
| --------------- | -------------------------------------: | -------: | --------: | ----------------------------------------------------------------------- |
| 127-130         |    `31-embodied-agent-loop-visualizer` |    IA 61 | 4 semanas | Visualizar observación, estado, acción, consecuencia y safety           |
| 131-135         | `32-robot-task-planning-control-board` |    IA 63 | 5 semanas | Mostrar objetivo, planner, control actions, feedback y error correction |
| 136-141         |       `33-humanoid-architecture-cards` |    IA 65 | 6 semanas | Crear tarjetas visuales de arquitectura humanoide                       |

Duración total del Plan 11:

```txt id="bp11-duration"
15 semanas
```

---

# 🧭 Filosofía de trabajo

Embodied AI y robótica pueden sonar futuristas, pero una explicación seria debe mostrar las piezas reales del sistema.

Este plan existe para explicar:

```txt id="bp11-philosophy"
qué observa el agente
qué recuerda
qué decide
qué acción intenta ejecutar
qué consecuencia aparece
qué feedback recibe
qué safety layer lo limita
qué arquitectura sostiene el sistema
```

Regla central:

```txt id="bp11-rule"
Un sistema encarnado no se entiende por su apariencia.
Se entiende por su ciclo percepción, memoria, acción, control y seguridad.
```

Un Building Project de Embodied AI y robótica debe ser:

```txt id="bp11-values"
visual
arquitectónico
responsable
explicable
documentado
terminable
```

No debe convertirse en hardware real ni en una plataforma robótica pesada.

Debe mostrar piezas conceptuales con claridad, estructura y límites.

---

# 🧩 Conceptos base

## Embodied Agent Loop

Un agente encarnado no solo responde texto.

Percibe un entorno, mantiene estado interno, toma decisiones y ejecuta acciones con consecuencias.

```txt id="bp11-agent-loop"
observación
→ estado interno
→ decisión
→ acción
→ consecuencia
→ feedback
```

---

## Perception

Percepción es transformar señales del entorno en información útil.

Puede venir de:

* cámaras;
* sensores conceptuales;
* posición;
* objetos visibles;
* instrucciones humanas;
* estado simulado.

---

## Memory

La memoria permite que el agente no dependa solo de la observación actual.

Puede guardar:

* objetos vistos;
* ubicaciones;
* acciones previas;
* objetivos;
* riesgos;
* estado de la tarea.

---

## Task Planning

Task planning convierte un objetivo en pasos.

Ejemplo:

```txt id="bp11-task-planning"
objetivo: mover objeto a la mesa
→ encontrar objeto
→ acercarse
→ tomar objeto
→ ir a mesa
→ soltar objeto
→ verificar
```

---

## Control

Control convierte una decisión en una acción ejecutable.

Puede incluir:

* avanzar;
* girar;
* tomar;
* soltar;
* ajustar;
* detenerse;
* corregir trayectoria.

---

## Safety Layer

La capa de seguridad limita acciones antes de ejecutarlas.

Ejemplo:

```txt id="bp11-safety"
acción solicitada
→ validación de seguridad
→ permitir / bloquear / pedir confirmación
```

---

## Humanoid Architecture

Una arquitectura humanoide no es solo una forma humana.

Incluye:

* cuerpo conceptual;
* sensores;
* actuadores;
* percepción;
* memoria;
* planificación;
* control;
* interacción humana;
* safety governance.

---

# 📁 Proyectos del Plan 11

---

## 31 — embodied-agent-loop-visualizer

### Match

```txt id="bp31-match"
AI Engineer Proyecto 61 — embodied-ai-foundations-lab
```

### Duración

```txt id="bp31-duration"
4 semanas
```

---

## 🧠 Descripción

Visualizador ligero del ciclo de un agente encarnado.

Este proyecto acompaña al proyecto de AI Engineer donde se estudian fundamentos de Embodied AI, diferencias entre chatbot y agente encarnado, entorno, observación, estado, acción, consecuencia y safety-first thinking.

Mientras AI Engineer profundiza en fundamentos conceptuales, este Building Project convierte el ciclo embodied en una visualización clara.

La idea es mostrar:

```txt id="bp31-core"
entorno
→ observación
→ estado interno
→ acción
→ consecuencia
→ feedback
→ safety notes
→ visualizer
```

Este proyecto no busca construir un robot.

Busca demostrar que puedo explicar qué hace diferente a un agente encarnado.

---

## 🎯 Objetivo

Crear un visualizador del ciclo entorno, observación, estado, acción, consecuencia y feedback.

El objetivo es explicar:

* qué observa el agente;
* qué estado interno mantiene;
* qué acciones puede tomar;
* qué consecuencia produce cada acción;
* qué feedback recibe;
* qué riesgos aparecen;
* qué acciones deberían bloquearse.

---

## 👤 Usuario objetivo

* Estudiante de Embodied AI.
* AI Engineer en formación.
* Persona interesada en agentes físicos o simulados.
* Reclutador técnico viendo evidencia de arquitectura AI + Robotics.
* Yo mismo como constructor de portafolio visual.

---

## 🧱 Arquitectura esperada

```txt id="bp31-architecture"
Environment
      ↓
Observation
      ↓
Internal State
      ↓
Action Options
      ↓
Consequence
      ↓
Feedback
      ↓
Safety Notes
      ↓
Loop Visualizer
```

---

## 🔁 Flujo técnico

```txt id="bp31-flow"
define environment
→ define observations
→ define internal state
→ define actions
→ simulate consequence
→ record feedback
→ render loop visualizer
```

---

## 🧩 Módulos

### Módulo 1 — Environment Card

Definir entorno.

Incluye:

* mundo simulado;
* objetos;
* agente;
* objetivo;
* restricciones;
* riesgos.

Pregunta central:

```txt id="bp31-q1"
¿En qué entorno existe el agente?
```

---

### Módulo 2 — Observation Card

Mostrar observación.

Incluye:

* objetos visibles;
* señales disponibles;
* posición;
* información incompleta;
* incertidumbre.

Pregunta central:

```txt id="bp31-q2"
¿Qué puede observar el agente y qué no puede ver?
```

---

### Módulo 3 — Internal State Card

Representar estado interno.

Incluye:

* objetivo actual;
* memoria corta;
* ubicación estimada;
* riesgos detectados;
* acciones previas.

Pregunta central:

```txt id="bp31-q3"
¿Qué sabe o cree saber el agente antes de actuar?
```

---

### Módulo 4 — Action Options

Listar acciones posibles.

Incluye:

* mover;
* esperar;
* acercarse;
* tomar objeto conceptual;
* pedir confirmación;
* acción bloqueada.

Pregunta central:

```txt id="bp31-q4"
¿Qué puede hacer el agente desde este estado?
```

---

### Módulo 5 — Consequence Viewer

Mostrar consecuencia.

Incluye:

* cambio de estado;
* éxito;
* fallo;
* riesgo;
* resultado inesperado.

Pregunta central:

```txt id="bp31-q5"
¿Qué pasó después de ejecutar la acción?
```

---

### Módulo 6 — Safety Notes

Documentar restricciones.

Incluye:

* acciones inseguras;
* incertidumbre alta;
* detenerse;
* pedir confirmación;
* bloqueo de acción.

Pregunta central:

```txt id="bp31-q6"
¿Qué debería impedir que el agente actúe?
```

---

### Módulo 7 — Loop Visualizer

Crear vista final.

Puede ser:

* `dashboard/README.md`;
* Streamlit simple;
* notebook visual;
* HTML ligero.

Debe mostrar:

* entorno;
* observación;
* estado;
* acción;
* consecuencia;
* feedback;
* safety notes.

Pregunta central:

```txt id="bp31-q7"
¿Puede alguien entender el ciclo embodied sin leer código?
```

---

## 🧪 Labs

### tec-labs

* `tec-environment-card-lab`
* `tec-observation-card-lab`
* `tec-internal-state-card-lab`
* `tec-action-options-lab`
* `tec-consequence-viewer-lab`
* `tec-safety-notes-lab`

### docs-labs

* `docs-embodied-agent-storytelling-lab`
* `docs-agent-loop-template-lab`

### cloud-labs

* `cloud-embodied-agent-notes-to-gcp-storage-lab`
* `cloud-embodied-agent-notes-to-aws-s3-lab`
* `cloud-embodied-agent-notes-to-azure-blob-lab`

---

## 📊 Métricas / Evidencia

* Environment cards.
* Observation cards.
* Internal state cards.
* Action cards.
* Consequence examples.
* Safety notes.
* Loop visualizer.
* Capturas.
* README profesional.

---

## 🚀 Estado actual

Pendiente / por iniciar.

---

## 🧭 Ciclo de trabajo

```txt id="bp31-cycle"
Semana 1 → Entorno, observación y estado interno
Semana 2 → Acciones, consecuencias y feedback
Semana 3 → Safety notes, loop visualizer y docs-labs
Semana 4 → Cloud-labs, README, capturas y cierre
```

---

## 📌 Próximos pasos

* Definir entorno pequeño.
* Crear tarjetas de observación.
* Crear tarjetas de estado interno.
* Definir acciones posibles.
* Simular consecuencias.
* Crear feedback notes.
* Crear safety notes.
* Preparar visualizer.
* Documentar labs.
* Agregar capturas.
* Publicar repo.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Embodied agent loop visualizer.
* Environment cards.
* Observation cards.
* Internal state cards.
* Action options.
* Consequence viewer.
* Safety notes.
* Labs documentados.
* README profesional.
* Capturas u outputs visibles.
* Conexión clara con `embodied-ai-foundations-lab`.

---

## 🧭 Regla final

```txt id="bp31-rule"
Un agente encarnado no solo responde.
Observa, recuerda, actúa y enfrenta consecuencias.

La acción siempre debe pasar por contexto y seguridad.
```

---

# 32 — robot-task-planning-control-board

### Match

```txt id="bp32-match"
AI Engineer Proyecto 63 — robot-task-planning-control-lab
```

### Duración

```txt id="bp32-duration"
5 semanas
```

---

## 🧠 Descripción

Tablero visual de planificación de tareas y control básico para robótica simulada.

Este proyecto acompaña al proyecto de AI Engineer donde se estudian task planning, goal decomposition, control loop, low-level actions, feedback, error correction y diferencia entre planner y controller.

Mientras AI Engineer profundiza en la lógica técnica, este Building Project crea un tablero visual para explicar cómo un objetivo se convierte en pasos, acciones y correcciones.

La idea es mostrar:

```txt id="bp32-core"
objetivo
→ planner
→ pasos
→ control actions
→ feedback
→ error correction
→ task board
```

Este proyecto no busca controlar un robot real.

Busca demostrar que puedo explicar la conexión entre intención, planificación y control.

---

## 🎯 Objetivo

Crear un tablero visual que muestre objetivo, planner, pasos, acciones de control, feedback y corrección de errores.

El objetivo es explicar:

* qué objetivo recibe el sistema;
* cómo se divide en pasos;
* qué acciones ejecutan esos pasos;
* qué feedback recibe;
* qué errores aparecen;
* cómo corrige o replantea;
* cuál es la diferencia entre planner y controller.

---

## 👤 Usuario objetivo

* Estudiante de robótica.
* AI Engineer en formación.
* Persona interesada en embodied AI.
* Reclutador técnico viendo planificación y control.
* Yo mismo como constructor de portafolio visual.

---

## 🧱 Arquitectura esperada

```txt id="bp32-architecture"
Goal
   ↓
Task Planner
   ↓
Steps
   ↓
Control Actions
   ↓
Environment Feedback
   ↓
Error Correction
   ↓
Planning Board
```

---

## 🔁 Flujo técnico

```txt id="bp32-flow"
define goal
→ decompose into steps
→ assign control actions
→ execute or simulate action
→ observe feedback
→ correct errors
→ render planning board
```

---

## 🧩 Módulos

### Módulo 1 — Goal Card

Definir objetivo.

Incluye:

* tarea principal;
* estado inicial;
* estado deseado;
* restricciones;
* criterio de éxito.

Pregunta central:

```txt id="bp32-q1"
¿Qué quiere lograr el robot o agente?
```

---

### Módulo 2 — Task Planner View

Dividir objetivo en pasos.

Incluye:

* subtareas;
* orden;
* precondiciones;
* dependencias;
* paso actual.

Pregunta central:

```txt id="bp32-q2"
¿Cómo convierto un objetivo en pasos ejecutables?
```

---

### Módulo 3 — Control Action Cards

Definir acciones de control.

Incluye:

* mover;
* girar;
* acercarse;
* esperar;
* tomar objeto conceptual;
* soltar objeto conceptual.

Pregunta central:

```txt id="bp32-q3"
¿Qué acciones concretas ejecutan el plan?
```

---

### Módulo 4 — Feedback Loop Viewer

Mostrar feedback.

Incluye:

* acción ejecutada;
* resultado observado;
* éxito;
* fallo;
* ajuste necesario.

Pregunta central:

```txt id="bp32-q4"
¿Cómo sabe el sistema si la acción funcionó?
```

---

### Módulo 5 — Error Correction Notes

Documentar corrección.

Incluye:

* reintento;
* cambio de paso;
* detención segura;
* replan;
* fallo repetido.

Pregunta central:

```txt id="bp32-q5"
¿Qué hace el sistema cuando el plan falla?
```

---

### Módulo 6 — Planner vs Controller Cards

Explicar diferencia.

Incluye:

* planner = qué hacer;
* controller = cómo ejecutarlo;
* feedback;
* replan;
* límites.

Pregunta central:

```txt id="bp32-q6"
¿Por qué planificación y control no son lo mismo?
```

---

### Módulo 7 — Task Board

Crear vista final.

Puede ser:

* `dashboard/README.md`;
* Streamlit simple;
* notebook visual;
* HTML ligero.

Debe mostrar:

* objetivo;
* pasos;
* acciones;
* feedback;
* errores;
* correcciones;
* explicación planner vs controller.

Pregunta central:

```txt id="bp32-q7"
¿Puede alguien entender la tarea robótica sin abrir código?
```

---

## 🧪 Labs

### tec-labs

* `tec-goal-card-lab`
* `tec-task-planner-view-lab`
* `tec-control-action-card-lab`
* `tec-feedback-loop-viewer-lab`
* `tec-error-correction-notes-lab`
* `tec-planner-vs-controller-card-lab`

### docs-labs

* `docs-robot-task-storytelling-lab`
* `docs-planning-control-template-lab`

### cloud-labs

* `cloud-task-planning-notes-to-gcp-storage-lab`
* `cloud-task-planning-notes-to-aws-s3-lab`
* `cloud-task-planning-notes-to-azure-blob-lab`

---

## 📊 Métricas / Evidencia

* Goal card.
* Task steps.
* Control action cards.
* Feedback loop.
* Error correction notes.
* Planner vs controller cards.
* Task board.
* Capturas.
* README profesional.

---

## 🚀 Estado actual

Pendiente / por iniciar.

---

## 🧭 Ciclo de trabajo

```txt id="bp32-cycle"
Semana 1 → Goal card, planner view y task steps
Semana 2 → Control action cards y feedback loop
Semana 3 → Error correction y planner vs controller cards
Semana 4 → Task board, docs-labs y capturas
Semana 5 → Cloud-labs, README final y cierre
```

---

## 📌 Próximos pasos

* Definir tarea pequeña.
* Crear goal card.
* Dividir objetivo en pasos.
* Crear control action cards.
* Crear feedback loop.
* Simular errores.
* Crear error correction notes.
* Crear planner vs controller cards.
* Preparar task board.
* Documentar labs.
* Agregar capturas.
* Publicar repo.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Robot task planning control board.
* Goal card.
* Task planner view.
* Control action cards.
* Feedback loop viewer.
* Error correction notes.
* Planner vs controller cards.
* Labs documentados.
* README profesional.
* Capturas u outputs visibles.
* Conexión clara con `robot-task-planning-control-lab`.

---

## 🧭 Regla final

```txt id="bp32-rule"
Planificar no es controlar.
Planificar decide qué hacer.
Controlar ejecuta cómo hacerlo.

Un sistema robótico necesita ambas capas.
```

---

# 33 — humanoid-architecture-cards

### Match

```txt id="bp33-match"
AI Engineer Proyecto 65 — humanoid-robotics-architecture-blueprint
```

### Duración

```txt id="bp33-duration"
6 semanas
```

---

## 🧠 Descripción

Tarjetas visuales de arquitectura para robótica humanoide.

Este proyecto acompaña al proyecto de AI Engineer donde se diseña un blueprint de arquitectura humanoide con cuerpo conceptual, sensores, actuadores, percepción, memoria, planificación, control, safety layer y plataforma.

Mientras AI Engineer profundiza en la arquitectura completa, este Building Project crea tarjetas visuales que explican cada capa de un sistema humanoide.

La idea es mostrar:

```txt id="bp33-core"
cuerpo conceptual
→ sensores
→ actuadores
→ percepción
→ memoria
→ planificación
→ control
→ safety
→ architecture cards
```

Este proyecto no busca construir un humanoide real.

Busca demostrar que puedo explicar humanoid robotics como arquitectura seria.

---

## 🎯 Objetivo

Crear tarjetas visuales de arquitectura humanoide.

El objetivo es explicar:

* qué partes tendría un cuerpo humanoide conceptual;
* qué sensores necesita;
* qué actuadores usaría;
* cómo percibe;
* cómo recuerda;
* cómo planifica;
* cómo controla;
* qué capa de seguridad limita sus acciones.

---

## 👤 Usuario objetivo

* Estudiante de robótica.
* AI Engineer en formación.
* Persona interesada en humanoides.
* Reclutador técnico viendo arquitectura AI + Robotics.
* Yo mismo como constructor de portafolio visual.

---

## 🧱 Arquitectura esperada

```txt id="bp33-architecture"
Humanoid Body Model
      ↓
Sensor Stack
      ↓
Actuator Stack
      ↓
Perception Layer
      ↓
Memory Layer
      ↓
Planning Layer
      ↓
Control Stack
      ↓
Safety Layer
      ↓
Architecture Cards
```

---

## 🔁 Flujo técnico

```txt id="bp33-flow"
define humanoid body concept
→ map sensors
→ map actuators
→ define perception layer
→ define memory layer
→ define planning layer
→ define control stack
→ define safety layer
→ export architecture cards
```

---

## 🧩 Módulos

### Módulo 1 — Humanoid Body Model Card

Definir cuerpo conceptual.

Incluye:

* cabeza;
* torso;
* brazos;
* manos;
* piernas;
* articulaciones;
* grados de libertad conceptuales.

Pregunta central:

```txt id="bp33-q1"
¿Qué partes del cuerpo humanoide deben modelarse?
```

---

### Módulo 2 — Sensor Stack Cards

Mapear sensores.

Incluye:

* cámaras;
* profundidad;
* micrófonos;
* IMU;
* tacto;
* fuerza;
* proximidad;
* estado interno.

Pregunta central:

```txt id="bp33-q2"
¿Qué necesita percibir un humanoide para actuar con seguridad?
```

---

### Módulo 3 — Actuator Stack Cards

Mapear actuadores.

Incluye:

* motores;
* servos conceptuales;
* articulaciones;
* manos;
* locomoción;
* límites físicos.

Pregunta central:

```txt id="bp33-q3"
¿Cómo se convierte una decisión en movimiento físico?
```

---

### Módulo 4 — Perception and Memory Cards

Explicar percepción y memoria.

Incluye:

* detección de objetos;
* localización;
* mapa interno;
* personas;
* objetos recordados;
* memoria de tarea.

Pregunta central:

```txt id="bp33-q4"
¿Cómo entiende el humanoide qué hay alrededor y qué recuerda?
```

---

### Módulo 5 — Planning and Control Cards

Explicar planificación y control.

Incluye:

* task planner;
* motion planner conceptual;
* control de articulaciones;
* feedback;
* replan;
* corrección.

Pregunta central:

```txt id="bp33-q5"
¿Cómo decide qué hacer y cómo lo ejecuta?
```

---

### Módulo 6 — Safety Layer Cards

Crear tarjetas de seguridad.

Incluye:

* límites de fuerza;
* zonas prohibidas;
* detección humana;
* parada segura;
* confirmación;
* bloqueo de acciones;
* monitoreo.

Pregunta central:

```txt id="bp33-q6"
¿Qué impide que el humanoide actúe de forma peligrosa?
```

---

### Módulo 7 — Architecture Portal

Crear vista final.

Puede ser:

* `dashboard/README.md`;
* portal estático;
* notebook visual;
* HTML ligero.

Debe mostrar:

* arquitectura por capas;
* tarjetas;
* diagramas;
* responsabilidades;
* límites.

Pregunta central:

```txt id="bp33-q7"
¿Puede alguien entender el humanoide como sistema completo?
```

---

## 🧪 Labs

### tec-labs

* `tec-humanoid-body-model-card-lab`
* `tec-sensor-stack-card-lab`
* `tec-actuator-stack-card-lab`
* `tec-perception-memory-card-lab`
* `tec-planning-control-card-lab`
* `tec-humanoid-safety-layer-card-lab`
* `tec-architecture-portal-lab`

### docs-labs

* `docs-humanoid-architecture-storytelling-lab`
* `docs-robotics-system-design-template-lab`

### cloud-labs

* `cloud-humanoid-architecture-docs-to-gcp-storage-lab`
* `cloud-humanoid-architecture-docs-to-aws-s3-lab`
* `cloud-humanoid-architecture-docs-to-azure-blob-lab`

---

## 📊 Métricas / Evidencia

* Body model card.
* Sensor stack cards.
* Actuator stack cards.
* Perception cards.
* Memory cards.
* Planning cards.
* Control cards.
* Safety layer cards.
* Architecture portal.
* Capturas.
* README profesional.

---

## 🚀 Estado actual

Pendiente / por iniciar.

---

## 🧭 Ciclo de trabajo

```txt id="bp33-cycle"
Semana 1 → Body model y sensor stack cards
Semana 2 → Actuator stack, perception y memory cards
Semana 3 → Planning, control y feedback cards
Semana 4 → Safety layer y architecture portal base
Semana 5 → Docs-labs, visual polish y capturas
Semana 6 → Cloud-labs, README final y cierre
```

---

## 📌 Próximos pasos

* Definir cuerpo humanoide conceptual.
* Crear tarjetas del cuerpo.
* Mapear sensores.
* Mapear actuadores.
* Crear tarjetas de percepción.
* Crear tarjetas de memoria.
* Crear tarjetas de planificación y control.
* Crear safety layer cards.
* Preparar architecture portal.
* Documentar labs.
* Agregar capturas.
* Publicar repo.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Humanoid architecture cards.
* Body model card.
* Sensor stack cards.
* Actuator stack cards.
* Perception and memory cards.
* Planning and control cards.
* Safety layer cards.
* Architecture portal.
* Labs documentados.
* README profesional.
* Capturas u outputs visibles.
* Conexión clara con `humanoid-robotics-architecture-blueprint`.

---

## 🧭 Regla final

```txt id="bp33-rule"
Un humanoide no es una forma humana con IA encima.
Es una arquitectura integrada de cuerpo, sensores, actuadores, percepción, memoria, control y seguridad.
```

---

# 🧱 Ciclo general de cada proyecto

Cada proyecto del Plan 11 sigue este ciclo:

```txt id="bp11-cycle-general"
1. Definir herramienta visual.
2. Definir usuario.
3. Definir qué concepto debe entenderse.
4. Elegir ejemplo o arquitectura pequeña.
5. Crear README inicial.
6. Crear estructura mínima.
7. Crear primera visualización.
8. Agregar tarjetas explicativas.
9. Crear labs pequeños.
10. Probar si aplica.
11. Documentar decisiones.
12. Agregar capturas.
13. Preparar demo o evidencia.
14. Escribir aprendizajes.
15. Definir limitaciones.
16. Definir siguiente paso.
17. Publicar en GitHub.
18. Conectar con el proyecto IA correspondiente.
```

---

# 🗂️ Estructura recomendada del repositorio

```txt id="bp11-repo-structure"
Embodied-AI-and-Robotics-Concepts/
├── 31-embodied-agent-loop-visualizer/
│   ├── data/
│   ├── src/
│   ├── reports/
│   ├── visuals/
│   ├── dashboard/
│   ├── docs/
│   ├── labs/
│   ├── scripts/
│   └── README.md
│
├── 32-robot-task-planning-control-board/
│   ├── data/
│   ├── src/
│   ├── reports/
│   ├── visuals/
│   ├── dashboard/
│   ├── docs/
│   ├── labs/
│   └── README.md
│
├── 33-humanoid-architecture-cards/
│   ├── docs/
│   ├── cards/
│   ├── visuals/
│   ├── reports/
│   ├── dashboard/
│   ├── labs/
│   └── README.md
│
└── README.md
```

---

# 📊 Nivel esperado al terminar Plan 11

| Área                              | Nivel esperado |
| --------------------------------- | -------------: |
| Embodied agent explanation        |         8.5/10 |
| Observation/state/action loop     |         8.5/10 |
| Consequence and feedback notes    |           8/10 |
| Safety notes for embodied AI      |         8.5/10 |
| Task planning visualization       |           8/10 |
| Planner vs controller explanation |         8.5/10 |
| Feedback loop visualization       |           8/10 |
| Error correction notes            |           8/10 |
| Humanoid architecture explanation |         8.5/10 |
| Sensor stack cards                |           8/10 |
| Actuator stack cards              |           8/10 |
| Safety layer cards                |         8.5/10 |
| README profesional                |         8.5/10 |
| Evidencia visual de aprendizaje   |           9/10 |

---

# 🧠 Resultado esperado del Plan 11

Al completar este plan, podré decir:

```txt id="bp11-result"
Sé explicar el ciclo de un agente encarnado.
Sé visualizar observación, memoria, acción y consecuencia.
Sé mostrar planificación de tareas robóticas.
Sé diferenciar planner y controller.
Sé explicar feedback y corrección de errores.
Sé crear tarjetas de arquitectura humanoide.
Sé explicar sensores, actuadores, percepción, memoria, control y safety.
Sé convertir Embodied AI y robótica en evidencia visual seria.
```

---

# 🧭 Regla final de avance

```txt id="bp11-final-rule"
Embodied AI no se demuestra con apariencia futurista.
Se demuestra con ciclo, arquitectura, control, feedback y seguridad.

Si el sistema actúa,
también debe poder detenerse, explicar y corregirse.
```

Frase guía:

```txt id="bp11-final-phrase"
AI Engineer me enseña embodied AI y robótica.
Building Projects me obliga a mostrar su arquitectura y comportamiento con claridad.
```

---

# 👤 Autor

**Jean Franck Loa Rojas**

Building Projects Path Builder
Embodied AI • Robotics Concepts • Humanoid Architecture • Task Planning • Control • Safety • Technical Storytelling
