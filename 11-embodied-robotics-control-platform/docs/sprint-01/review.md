# Sprint 1 closure review

## Acceptance evidence

Run `scripts/run-quality-gate.ps1` from the project root. The gate checks Python contracts and source, TypeScript and web tests, pinned container builds, URDF/Xacro, C++ safety rules, a real Gazebo-to-ROS action, persisted TimescaleDB samples and loop events, read-only replay, Chrome flows and an automated accessibility audit. It stops the test stack without deleting the database volume. A passing run is necessary before the sprint tag is created.

The scenario `sim/scenarios/studio-joint-motion.v1.json` fixes the world, robot, seed, target and tolerance. `sim/assets/manifest.v1.json` records SHA-256 for the local robot/world assets. The run ID changes on each simulator start; the API keeps prior runs separate and lists them for read-only replay. The smoke test verifies that reading replay neither changes the live run ID nor rewinds its state sequence.

## Boundary review

- **Provenance:** the robot pose originates in Gazebo, crosses the ROS bridge, and is serialized through gRPC and WebSocket. The browser does not synthesize a pose when the stream is absent.
- **Authority:** the simulated ROS Action requires the separate C++ supervisor. Duplicate sequence and out-of-range targets fail closed. This is not physical safety certification.
- **Observability:** perception, state, bounded memory, typed intent, safety, dispatched action and observed feedback have one correlation ID. Replay reads persisted records; it does not send an action.
- **Accessibility:** current status is conveyed by text, not color alone. A link-position table remains available without WebGL; the gate exercises keyboard, mobile and axe checks.
- **Scope:** one articulated shoulder in a small headless world. No camera detections, external AI model, hardware control, autonomous multi-step planner or public command endpoint is claimed. Those are not used to manufacture Sprint 1 evidence.

## Operational limits and follow-up

- The replay API currently returns at most 500 samples per page. The UI presents the first page of a selected run; larger runs need pagination or server-side time-window queries in a later iteration.
- The R3F scene uses simplified link geometry at the measured transforms; it is a state visualizer, not a photorealistic mesh or a collision safety display.
- The UI observes only a local simulation. It does not provide authentication or remote control and must not be exposed as a production service without a separate security review.
- The frontend build reports a large JavaScript chunk; code splitting is a performance follow-up, not a claim about the simulation result.
- One complete local gate run printed a transient Python `Cannot allocate memory` message from an auxiliary container process while Docker Desktop had a roughly 1.9 GiB memory limit. The action smoke, service health checks and all browser tests still passed. Increase Docker's memory allowance before treating this as a robust stress-test environment; the gate does not certify low-memory operation.

No Azure deployment or external release is part of this local sprint acceptance. Git tags and remote publication must be verified separately from the passing test result.
