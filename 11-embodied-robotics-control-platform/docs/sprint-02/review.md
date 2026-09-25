# Sprint 2 verification and release boundary

The implemented vertical slice is a local, supervised **simulation** control board. A typed joint goal becomes `task-plan.v1`, is bound to a live world snapshot, waits for operator approval and an exclusive ROS-side lease, then travels through gRPC and a ROS Action to Gazebo. Action feedback and terminal results are correlated with a persisted audit. The control board exposes Stop, Cancel and latched EStop separately, and replay cannot issue commands.

`scripts/run-quality-gate.ps1` verifies Python lint/format/tests, TypeScript build and tests, Compose build, URDF/Xacro, C++ supervisor GoogleTests, the original Sprint 1 real-action smoke, Sprint 2 plan/approval/execution, terminal ROS cancellation, an EStop injected during an active action, local API latency samples and six Playwright flows including mobile and axe accessibility. The gate stops containers without removing the database volume. The latency script reports p50/p95/p99 for 20 status reads and 10 plan+audit writes; this is a single-client local smoke, **not** a load or control-cycle benchmark.

## Items preventing the full roadmap Definition of Done

- P62/P63 currently contain only README placeholders. No versioned `EmbodiedEvidenceBundle`, checksums, model cards or frame semantics are available to import, so importer compatibility and perception/world association cannot be honestly marked complete.
- The scenario has one shoulder joint and a bounded setpoint increment. It does not implement an independent velocity/acceleration envelope, workspace/collision zones or hardware watchdog. The C++ supervisor handles lease, mode, target, sequence and EStop; it is not a certified physical safety component.
- Sensor-loss, delayed-feedback and blocked-action fault drills, plus a larger replay/load trace, remain outside the currently verified EStop/cancellation drills.
- Render, ROS loop and DB ingestion under concurrency have not been profiled; the local HTTP latency smoke does not substitute for those measurements. The WebGL twin is lazy-loaded (the main bundle drops from roughly 1.16 MB to 250 kB minified), but its separate 3D chunk still triggers a large-chunk warning and needs measured browser profiling.
- No external voice/vision intent is accepted. Typed human input remains the only goal source; multimodal intent must stay a proposal-only boundary when real P62/P63 artifacts arrive.

Consequently, a passing **core** quality gate is not a claim that every roadmap item is complete. Do not create `v0.2.0-sprint-02-robot-task-planning-control-board` or publish a Sprint 2 release until these gaps are either implemented and verified or explicitly re-scoped with the user. No Azure resources or physical hardware are part of this work.
