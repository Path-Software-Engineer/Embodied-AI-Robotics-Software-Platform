# 11-embodied-ai-robotics-platform

## 🧠 Descripción

**Embodied AI Robotics Platform** es una plataforma de software visual para explicar agentes encarnados, planificación robótica, control básico, feedback, corrección de errores y arquitectura humanoide.

Este proyecto pertenece a la ruta:

```txt
Path Software Engineer
```

y acompaña directamente al plan:

```txt
Path AI Engineer Plan 11 — Embodied AI, Humanoid Robotics & Android Systems
```

Mientras Path AI Engineer profundiza en percepción, memoria, acción, task planning, control loop, safety layer y arquitectura humanoide, este proyecto convierte esos conceptos en una aplicación visual, clara, documentada y publicable.

La idea es mostrar:

```txt
entorno
→ observación
→ estado interno
→ acción
→ consecuencia
→ feedback
→ planificación
→ control
→ safety
→ arquitectura humanoide
→ plataforma visual
```

Este proyecto no busca construir un robot real.

Busca demostrar que puedo explicar sistemas encarnados y robóticos como software serio, visual, modular y responsable.

---

## 🎯 Objetivo

Crear una plataforma que permita visualizar y explicar:

- el ciclo de un agente encarnado;
- el entorno donde existe;
- lo que observa;
- su estado interno;
- sus acciones posibles;
- las consecuencias de sus acciones;
- el feedback que recibe;
- los riesgos y acciones bloqueadas;
- la planificación de tareas robóticas;
- la diferencia entre planner y controller;
- la corrección de errores;
- la arquitectura de un humanoide conceptual.

---

## 👤 Usuario objetivo

- Estudiante de Embodied AI.
- Estudiante de robótica.
- AI Engineer en formación.
- Persona interesada en agentes físicos o simulados.
- Reclutador técnico viendo evidencia de arquitectura AI + Robotics.
- Yo mismo como constructor de portafolio visual.

---

## 🧱 Arquitectura esperada

```txt
Embodied AI Robotics Platform
      ↓
Frontend Dashboard
      ↓
Backend API
      ↓
AI Services
      ↓
Simulation Services
      ↓
Reports / Cards / Visuals
      ↓
Docs / Labs / Evidence
```

## 🗂️ Estructura esperada

```txt
11-embodied-ai-robotics-platform/
│
├── frontend/
├── backend/
├── ai-services/
├── simulation-services/
├── data/
├── reports/
├── docs/
├── labs/
├── tests/
├── scripts/
└── deployment/
```

---

## 🔁 Flujo técnico general

```txt
define scenario
→ load environment
→ define observations
→ update internal state
→ choose action
→ simulate consequence
→ capture feedback
→ apply safety rules
→ create visual card
→ export dashboard/report
```

---

# 🏃 Sprints del proyecto

## Sprint 1 — Embodied Agent Loop Module

### 🧠 Descripción

Visualizador ligero del ciclo de un agente encarnado.

Este sprint convierte el concepto de Embodied AI en una secuencia visual:

```txt
Environment
→ Observation
→ Internal State
→ Action Options
→ Consequence
→ Feedback
→ Safety Notes
→ Loop Visualizer
```

### 🎯 Objetivo

Crear un visualizador del ciclo entorno, observación, estado, acción, consecuencia y feedback.

El objetivo es explicar:

- qué observa el agente;
- qué estado interno mantiene;
- qué acciones puede tomar;
- qué consecuencia produce cada acción;
- qué feedback recibe;
- qué riesgos aparecen;
- qué acciones deberían bloquearse.

### 🧩 Módulos

#### Módulo 1 — Environment Card

Define el entorno donde existe el agente.

Incluye:

- mundo simulado;
- objetos;
- agente;
- objetivo;
- restricciones;
- riesgos.

Pregunta central:

```txt
¿En qué entorno existe el agente?
```

---

#### Módulo 2 — Observation Card

Muestra lo que el agente puede observar.

Incluye:

- objetos visibles;
- señales disponibles;
- posición;
- información incompleta;
- incertidumbre.

Pregunta central:

```txt
¿Qué puede observar el agente y qué no puede ver?
```

---

#### Módulo 3 — Internal State Card

Representa el estado interno del agente.

Incluye:

- objetivo actual;
- memoria corta;
- ubicación estimada;
- riesgos detectados;
- acciones previas.

Pregunta central:

```txt
¿Qué sabe o cree saber el agente antes de actuar?
```

---

#### Módulo 4 — Action Options

Lista acciones posibles.

Incluye:

- mover;
- esperar;
- acercarse;
- tomar objeto conceptual;
- pedir confirmación;
- acción bloqueada.

Pregunta central:

```txt
¿Qué puede hacer el agente desde este estado?
```

---

#### Módulo 5 — Consequence Viewer

Muestra qué ocurre después de ejecutar una acción.

Incluye:

- cambio de estado;
- éxito;
- fallo;
- riesgo;
- resultado inesperado.

Pregunta central:

```txt
¿Qué pasó después de ejecutar la acción?
```

---

#### Módulo 6 — Safety Notes

Documenta restricciones y acciones inseguras.

Incluye:

- acciones inseguras;
- incertidumbre alta;
- detenerse;
- pedir confirmación;
- bloqueo de acción.

Pregunta central:

```txt
¿Qué debería impedir que el agente actúe?
```

---

#### Módulo 7 — Loop Visualizer

Crea la vista final del ciclo embodied.

Debe mostrar:

- entorno;
- observación;
- estado;
- acción;
- consecuencia;
- feedback;
- safety notes.

Pregunta central:

```txt
¿Puede alguien entender el ciclo embodied sin leer código?
```

### 🧪 Labs

#### tec-labs

- `tec-environment-card-lab`
- `tec-observation-card-lab`
- `tec-internal-state-card-lab`
- `tec-action-options-lab`
- `tec-consequence-viewer-lab`
- `tec-safety-notes-lab`

#### docs-labs

- `docs-embodied-agent-storytelling-lab`
- `docs-agent-loop-template-lab`

#### cloud-labs

- `cloud-embodied-agent-notes-to-gcp-storage-lab`
- `cloud-embodied-agent-notes-to-aws-s3-lab`
- `cloud-embodied-agent-notes-to-azure-blob-lab`

### 📊 Evidencia esperada

- Environment cards.
- Observation cards.
- Internal state cards.
- Action cards.
- Consequence examples.
- Safety notes.
- Loop visualizer.
- Capturas.
- README actualizado.

---

## Sprint 2 — Robot Task Planning & Control Module

### 🧠 Descripción

Tablero visual de planificación de tareas y control básico para robótica simulada.

Este sprint explica cómo un objetivo se convierte en pasos, acciones concretas, feedback y corrección.

```txt
Goal
→ Task Planner
→ Steps
→ Control Actions
→ Environment Feedback
→ Error Correction
→ Planning Board
```

### 🎯 Objetivo

Crear un tablero visual que muestre objetivo, planner, pasos, acciones de control, feedback y corrección de errores.

El objetivo es explicar:

- qué objetivo recibe el sistema;
- cómo se divide en pasos;
- qué acciones ejecutan esos pasos;
- qué feedback recibe;
- qué errores aparecen;
- cómo corrige o replantea;
- cuál es la diferencia entre planner y controller.

### 🧩 Módulos

#### Módulo 1 — Goal Card

Define el objetivo de la tarea.

Incluye:

- tarea principal;
- estado inicial;
- estado deseado;
- restricciones;
- criterio de éxito.

Pregunta central:

```txt
¿Qué quiere lograr el robot o agente?
```

---

#### Módulo 2 — Task Planner View

Divide el objetivo en pasos.

Incluye:

- subtareas;
- orden;
- precondiciones;
- dependencias;
- paso actual.

Pregunta central:

```txt
¿Cómo convierto un objetivo en pasos ejecutables?
```

---

#### Módulo 3 — Control Action Cards

Define acciones concretas.

Incluye:

- mover;
- girar;
- acercarse;
- esperar;
- tomar objeto conceptual;
- soltar objeto conceptual.

Pregunta central:

```txt
¿Qué acciones concretas ejecutan el plan?
```

---

#### Módulo 4 — Feedback Loop Viewer

Muestra feedback después de la acción.

Incluye:

- acción ejecutada;
- resultado observado;
- éxito;
- fallo;
- ajuste necesario.

Pregunta central:

```txt
¿Cómo sabe el sistema si la acción funcionó?
```

---

#### Módulo 5 — Error Correction Notes

Documenta cómo responde el sistema al fallo.

Incluye:

- reintento;
- cambio de paso;
- detención segura;
- replan;
- fallo repetido.

Pregunta central:

```txt
¿Qué hace el sistema cuando el plan falla?
```

---

#### Módulo 6 — Planner vs Controller Cards

Explica diferencia entre planificación y control.

Incluye:

- planner = qué hacer;
- controller = cómo ejecutarlo;
- feedback;
- replan;
- límites.

Pregunta central:

```txt
¿Por qué planificación y control no son lo mismo?
```

---

#### Módulo 7 — Task Board

Crea la vista final.

Debe mostrar:

- objetivo;
- pasos;
- acciones;
- feedback;
- errores;
- correcciones;
- planner vs controller.

Pregunta central:

```txt
¿Puede alguien entender la tarea robótica sin abrir código?
```

### 🧪 Labs

#### tec-labs

- `tec-goal-card-lab`
- `tec-task-planner-view-lab`
- `tec-control-action-card-lab`
- `tec-feedback-loop-viewer-lab`
- `tec-error-correction-notes-lab`
- `tec-planner-vs-controller-card-lab`

#### docs-labs

- `docs-robot-task-storytelling-lab`
- `docs-planning-control-template-lab`

#### cloud-labs

- `cloud-task-planning-notes-to-gcp-storage-lab`
- `cloud-task-planning-notes-to-aws-s3-lab`
- `cloud-task-planning-notes-to-azure-blob-lab`

### 📊 Evidencia esperada

- Goal card.
- Task steps.
- Control action cards.
- Feedback loop.
- Error correction notes.
- Planner vs controller cards.
- Task board.
- Capturas.
- README actualizado.

---

## Sprint 3 — Humanoid Architecture Module

### 🧠 Descripción

Tarjetas visuales de arquitectura para robótica humanoide.

Este sprint explica un sistema humanoide como arquitectura integrada de cuerpo conceptual, sensores, actuadores, percepción, memoria, planificación, control y seguridad.

```txt
Humanoid Body Model
→ Sensor Stack
→ Actuator Stack
→ Perception Layer
→ Memory Layer
→ Planning Layer
→ Control Stack
→ Safety Layer
→ Architecture Cards
```

### 🎯 Objetivo

Crear tarjetas visuales de arquitectura humanoide.

El objetivo es explicar:

- qué partes tendría un cuerpo humanoide conceptual;
- qué sensores necesita;
- qué actuadores usaría;
- cómo percibe;
- cómo recuerda;
- cómo planifica;
- cómo controla;
- qué capa de seguridad limita sus acciones;
- cómo se conectan hardware conceptual y software.

### 🧩 Módulos

#### Módulo 1 — Humanoid Body Model Card

Define el cuerpo conceptual.

Incluye:

- cabeza;
- torso;
- brazos;
- manos;
- piernas;
- articulaciones;
- grados de libertad conceptuales.

Pregunta central:

```txt
¿Qué partes del cuerpo humanoide deben modelarse?
```

---

#### Módulo 2 — Sensor Stack Cards

Mapea sensores.

Incluye:

- cámaras;
- profundidad;
- micrófonos;
- IMU;
- tacto;
- fuerza;
- proximidad;
- estado interno.

Pregunta central:

```txt
¿Qué necesita percibir un humanoide para actuar con seguridad?
```

---

#### Módulo 3 — Actuator Stack Cards

Mapea actuadores.

Incluye:

- motores;
- servos conceptuales;
- articulaciones;
- manos;
- locomoción;
- límites físicos.

Pregunta central:

```txt
¿Cómo se convierte una decisión en movimiento físico?
```

---

#### Módulo 4 — Perception and Memory Cards

Explica percepción y memoria.

Incluye:

- detección de objetos;
- localización;
- mapa interno;
- personas;
- objetos recordados;
- memoria de tarea.

Pregunta central:

```txt
¿Cómo entiende el humanoide qué hay alrededor y qué recuerda?
```

---

#### Módulo 5 — Planning and Control Cards

Explica planificación y control.

Incluye:

- task planner;
- motion planner conceptual;
- control de articulaciones;
- feedback;
- replan;
- corrección.

Pregunta central:

```txt
¿Cómo decide qué hacer y cómo lo ejecuta?
```

---

#### Módulo 6 — Safety Layer Cards

Crea tarjetas de seguridad.

Incluye:

- límites de fuerza;
- zonas prohibidas;
- detección humana;
- parada segura;
- confirmación;
- bloqueo de acciones;
- monitoreo.

Pregunta central:

```txt
¿Qué impide que el humanoide actúe de forma peligrosa?
```

---

#### Módulo 7 — Architecture Portal

Crea la vista final.

Debe mostrar:

- arquitectura por capas;
- tarjetas;
- diagramas;
- responsabilidades;
- límites.

Pregunta central:

```txt
¿Puede alguien entender el humanoide como sistema completo?
```

### 🧪 Labs

#### tec-labs

- `tec-humanoid-body-model-card-lab`
- `tec-sensor-stack-card-lab`
- `tec-actuator-stack-card-lab`
- `tec-perception-memory-card-lab`
- `tec-planning-control-card-lab`
- `tec-humanoid-safety-layer-card-lab`
- `tec-architecture-portal-lab`

#### docs-labs

- `docs-humanoid-architecture-storytelling-lab`
- `docs-robotics-system-design-template-lab`

#### cloud-labs

- `cloud-humanoid-architecture-docs-to-gcp-storage-lab`
- `cloud-humanoid-architecture-docs-to-aws-s3-lab`
- `cloud-humanoid-architecture-docs-to-azure-blob-lab`

### 📊 Evidencia esperada

- Body model card.
- Sensor stack cards.
- Actuator stack cards.
- Perception and memory cards.
- Planning and control cards.
- Safety layer cards.
- Architecture portal.
- Capturas.
- README actualizado.

---

# 📊 Métricas / Evidencia general

Este proyecto puede generar:

- visualización del ciclo embodied;
- environment cards;
- observation cards;
- internal state cards;
- action cards;
- consequence examples;
- safety notes;
- goal cards;
- task planner view;
- control action cards;
- feedback loop;
- error correction notes;
- planner vs controller cards;
- humanoid body model cards;
- sensor stack cards;
- actuator stack cards;
- perception and memory cards;
- planning and control cards;
- safety layer cards;
- architecture portal;
- reports;
- capturas;
- README profesional.

---

# 🚀 Estado actual

Pendiente / por iniciar.

---

# 🧭 Ciclo de trabajo

```txt
Sprint 1 → Embodied agent loop, consequences, feedback y safety notes
Sprint 2 → Task planning, control actions, feedback loop y error correction
Sprint 3 → Humanoid architecture cards, architecture portal y cierre
```

---

# 📌 Próximos pasos

- Definir estructura base del proyecto.
- Crear documentación inicial.
- Crear user stories.
- Crear technical stories.
- Definir primer entorno pequeño.
- Crear environment card.
- Crear observation card.
- Crear internal state card.
- Definir acciones posibles.
- Simular consecuencias.
- Crear safety notes.
- Preparar primer visualizer.
- Documentar labs.
- Agregar capturas.
- Publicar repo.

---

# ✅ Entregable final

Al terminar este proyecto debe existir:

- Embodied AI Robotics Platform;
- Embodied Agent Loop Module;
- Robot Task Planning & Control Module;
- Humanoid Architecture Module;
- frontend;
- backend;
- AI services;
- simulation services;
- visual cards;
- task board;
- architecture portal;
- safety notes;
- labs documentados;
- README profesional;
- capturas u outputs visibles;
- conexión clara con `embodied-ai-foundations-lab`, `robot-task-planning-control-lab` y `humanoid-robotics-architecture-blueprint`.

---

# 🧭 Regla final

```txt
Un sistema encarnado no se entiende por su apariencia.
Se entiende por lo que observa, recuerda, decide, ejecuta, corrige y bloquea.

Si el sistema actúa,
también debe poder detenerse, explicar y corregirse.
```

Este proyecto debe demostrar que puedo convertir Embodied AI y robótica en una plataforma visual, seria y responsable.

---

# 👤 Autor

**Jean Franck Loa Rojas**

Path Software Engineer Builder  
Embodied AI • Robotics Concepts • Humanoid Architecture • Task Planning • Control • Safety • Product Architecture • Technical Documentation
