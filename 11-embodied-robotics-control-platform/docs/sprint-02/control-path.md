# Sprint 2 control path and contract

The control board is a **local, simulation-only** operator surface. It cannot publish to ROS directly. Its sole motion path is:

```text
typed goal → HTTP proposal → gRPC deterministic planner → versioned TaskPlan
           → operator approval + exclusive lease + fresh snapshot
           → gRPC executor → ROS MoveJoint Action → C++ Safety Supervisor
           → Gazebo joint command → observed ROS feedback → Timescale audit/replay
```

`task-plan.v1` contains the run/robot, snapshot sequence/time/hash, source, and a bounded graph of one to four nodes. Only `move_joint` on the simulated `left_shoulder` is currently planned. Targets are limited to ±0.8 rad, each node requires human approval, and the only failure policy is `stop`. Before approval and dispatch, the gateway rechecks run, robot, pose drift (≤0.05 rad), freshness (≤1 s), monotonic state sequence and the 120 s approval window. A plan is never an authorization.

The operator token stays in the PowerShell process and in browser tab memory, not in the web bundle or database. An `X-Actor-Id` is recorded for attribution, but this local shared-token setup does **not** provide individually authenticated identities. Do not expose the command API to an untrusted network. Read-only observation and replay do not require the operator token; every mutation does.

The C++ supervisor is separate from the gateway, planner and database. A lease is exclusive per simulated run, lasts at most 30 s and must be renewed. Modes progress Disarmed → Manual → Assisted → AutonomousSim (and back one level), with explicit confirmation. Status reads expire old leases and disarm. The ROS Action checks lease/mode/EStop during movement; loss aborts and requests hold-current-position. Stop disarms; cancel requests ROS Action cancellation; EStop latches and clears the lease; reset leaves the robot disarmed. These are **software simulation controls, not a physical E-stop or certified safety function**.

The Action has bounded feedback and an 8 s execution timeout. Correlation uses the plan ID through ROS loop events and persisted `control_events`; replay never dispatches a command. Database failure denies plan or audit operations but does not grant motion authority.

## Explicit limits

- The AI Engineer P62/P63 directories currently provide no executable, versioned evidence bundle. No detections, model weights, or raw media were imported or run. The single shoulder goal is typed by the operator; no voice/vision input is accepted as authority.
- No physical robot, controller velocity/acceleration envelope, collision-zone model, camera perception, or hardware watchdog is represented by this small Gazebo scenario. The ±0.8 rad joint and pose-drift constraints do not imply those absent protections.
- Gateway and ROS containers share a trusted local Compose network. A production deployment would need identity-bound credentials, mTLS/transport isolation, stronger rate limiting, and an independent hazard assessment.
- The quality gate includes a single-client local latency smoke (20 supervisor reads and 10 plan+audit persistence requests). It reports p50/p95/p99 and enforces loose p95 budgets of 2 s/3 s respectively. This is not a concurrency, WebGL render, ROS control-cycle, or capacity benchmark.
