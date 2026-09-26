# Sprint 3 architecture studio — verification and release boundary

## Implemented vertical slice

`architecture/manifest.v1.json` is the versioned system catalog. Its schema and validator reject malformed entries, missing source files, unsafe paths, orphan interfaces/components and controls pointing outside the catalog. The validator hashes every linked source/contract/test file. The gateway exposes read-only `/api/v3/architecture/manifest`, `/health` and `/snapshots` endpoints; startup records each distinct manifest digest in TimescaleDB. The React studio displays components, protocol edges, control authority, source digests, residual risks, observed runtime health and explicit evidence gaps. The `AndroidArchitectureEvidenceContract` is a read-only, versioned export for a future Project 66 blueprint; it authorizes no command or cross-repository modification.

The eight browser flows include architecture selection, narrow mobile viewport and an axe audit. The existing supervised control/ROS/Gazebo/EStop smokes remain part of the gate. A successful gate demonstrates this **architecture vertical slice**, not the complete five-week Sprint 3 Definition of Done.

## Source and evidence limits

- The actual AI Engineer folders are `64-human-robot-interaction-safety-lab` and `65-humanoid-robotics-architecture-blueprint`, whereas the supplied Software Engineer map calls P64 a task-planning simulator and P65 an edge deployment lab. Both actual folders currently have only README files; no versioned scenarios, edge profiles, planner traces, model manifests or measurements can be imported. The catalog marks both unavailable rather than synthesizing evidence.
- The `local-compose` profile has functional simulation smoke only. CPU/GPU/memory/storage/power/thermal measurements, constrained-device profiles and network fault measurements have not been produced. `embedded-target` remains `not-measured`.
- The source catalog documents seven observed interfaces, but it is not yet an automated extractor for the full live ROS graph or a QoS/deadline profiler. No signed reversible deployment bundle, SBOM or rollback drill is claimed.
- Three hazards are source-linked to controls and test paths. Their presence does not prove comprehensive hazard analysis or safety certification; sensor-loss/delayed-feedback, HRI zone, security abuse, failover and multimodal ambiguity suites remain open.
- Health is limited to simulation sample age, telemetry DB state and dropped writes. Distributed cross-protocol trace, recovery-time measurement, DB backup/restore and load/performance gates are not complete.
- Sprint 2 still has the blockers documented in `docs/sprint-02/review.md`. Consequently the Sprint 2 tag is not present, and this stacked Sprint 3 feature branch is not ready to merge/release as v1.0.0.

## Safe local verification

```powershell
Set-Location "C:\JeanLoa\Path-Software-Engineer\Embodied-AI-Robotics-Software-Platform\11-embodied-robotics-control-platform"
.\scripts\run-quality-gate.ps1
```

The gate starts local containers and stops them afterwards without deleting the TimescaleDB volume. It does not deploy to Azure or touch physical hardware. Do not tag `v1.0.0-embodied-robotics-control-platform` until the full map Definition of Done, missing AI evidence boundaries, security/performance/restore tests and release integration are actually verified.
