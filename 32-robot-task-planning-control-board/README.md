# 32-robot-task-planning-control-board

## 🧠 Descripción

Tablero visual de planificación de tareas y control básico para robótica simulada.

Este proyecto pertenece a la ruta:

```txt id="bp32-route"
Building Projects
```

y acompaña directamente al proyecto:

```txt id="bp32-match"
AI Engineer Proyecto 63 — robot-task-planning-control-lab
```

Mientras AI Engineer profundiza en task planning, goal decomposition, control loop, low-level actions, feedback, error correction y diferencia entre planner y controller, este Building Project crea un tablero visual para explicar cómo un objetivo se convierte en pasos, acciones y correcciones.

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

* Qué objetivo recibe el sistema.
* Cómo se divide en pasos.
* Qué acciones ejecutan esos pasos.
* Qué feedback recibe.
* Qué errores aparecen.
* Cómo corrige o replantea.
* Cuál es la diferencia entre planner y controller.

---

## 👤 Usuario objetivo

* Estudiante de robótica.
* AI Engineer en formación.
* Persona interesada en Embodied AI.
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

* Tarea principal.
* Estado inicial.
* Estado deseado.
* Restricciones.
* Criterio de éxito.

Pregunta central:

```txt id="bp32-q1"
¿Qué quiere lograr el robot o agente?
```

---

### Módulo 2 — Task Planner View

Dividir objetivo en pasos.

Incluye:

* Subtareas.
* Orden.
* Precondiciones.
* Dependencias.
* Paso actual.

Pregunta central:

```txt id="bp32-q2"
¿Cómo convierto un objetivo en pasos ejecutables?
```

---

### Módulo 3 — Control Action Cards

Definir acciones de control.

Incluye:

* Mover.
* Girar.
* Acercarse.
* Esperar.
* Tomar objeto conceptual.
* Soltar objeto conceptual.

Pregunta central:

```txt id="bp32-q3"
¿Qué acciones concretas ejecutan el plan?
```

---

### Módulo 4 — Feedback Loop Viewer

Mostrar feedback.

Incluye:

* Acción ejecutada.
* Resultado observado.
* Éxito.
* Fallo.
* Ajuste necesario.

Pregunta central:

```txt id="bp32-q4"
¿Cómo sabe el sistema si la acción funcionó?
```

---

### Módulo 5 — Error Correction Notes

Documentar corrección.

Incluye:

* Reintento.
* Cambio de paso.
* Detención segura.
* Replan.
* Fallo repetido.

Pregunta central:

```txt id="bp32-q5"
¿Qué hace el sistema cuando el plan falla?
```

---

### Módulo 6 — Planner vs Controller Cards

Explicar diferencia.

Incluye:

* Planner = qué hacer.
* Controller = cómo ejecutarlo.
* Feedback.
* Replan.
* Límites.

Pregunta central:

```txt id="bp32-q6"
¿Por qué planificación y control no son lo mismo?
```

---

### Módulo 7 — Safety Check Notes

Agregar validación de seguridad básica.

Incluye:

* Acción permitida.
* Acción bloqueada.
* Riesgo del entorno.
* Confirmación.
* Detención segura.

Pregunta central:

```txt id="bp32-q7"
¿Qué debe revisarse antes de ejecutar una acción?
```

---

### Módulo 8 — Task Board

Crear vista final.

Puede ser:

* `dashboard/README.md`.
* Streamlit simple.
* Notebook visual.
* HTML ligero.

Debe mostrar:

* Objetivo.
* Pasos.
* Acciones.
* Feedback.
* Errores.
* Correcciones.
* Explicación planner vs controller.

Pregunta central:

```txt id="bp32-q8"
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
* `tec-safety-check-notes-lab`

### docs-labs

* `docs-robot-task-storytelling-lab`
* `docs-planning-control-template-lab`

### cloud-labs

* `cloud-task-planning-notes-to-gcp-storage-lab`
* `cloud-task-planning-notes-to-aws-s3-lab`
* `cloud-task-planning-notes-to-azure-blob-lab`

---

## 📊 Métricas / Evidencia

Este proyecto puede generar:

* Goal card.
* Task steps.
* Control action cards.
* Feedback loop.
* Error correction notes.
* Planner vs controller cards.
* Safety check notes.
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
Semana 3 → Error correction, safety check y planner vs controller cards
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
* Crear safety check notes.
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
* Safety check notes.
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

Un sistema robótico necesita ambas capas, más feedback y seguridad.
```

Este proyecto debe demostrar que puedo explicar una tarea robótica como sistema de planificación, control, feedback y corrección.
