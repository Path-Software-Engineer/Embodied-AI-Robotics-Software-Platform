# Sprint 2 simulation safety case v1

This is a test traceability record, **not a claim of certified or physical safety**. Evidence is reproduced by `scripts/run-quality-gate.ps1` and `scripts/run-control-smoke.ps1`.

| Hazard | Independent control | Verification | Residual risk |
| --- | --- | --- | --- |
| Concurrent operators command one joint | Exclusive C++ lease, owner check and expiration | `LeaseOwnershipModeTransitionsAndLatchedEStop`, HTTP control smoke | Shared bearer token does not bind a real human identity |
| Stale/other-run plan executes | Snapshot, run/frame/sequence/freshness/pose checks | `tests/test_planning.py`; HTTP proposal→approval→execution | Snapshot is a software observation, not a redundant sensor |
| Out-of-range or duplicate motion | C++ ROS-side target and sequence guard | `RejectsOutOfRangeNonFiniteAndWrongScope`, Sprint 1 ROS smoke | No dynamic velocity, acceleration or collision envelope |
| Loss of UI or heartbeat during action | Timed lease and ROS Action authority poll, abort/hold request | `StatusDisarmsExpiredLeaseAndHeartbeatRequiresOwner`; Action smoke | Hold is a request through simulation; no independent actuator cut-off |
| Unsafe mode transition | C++ state machine; explicit operator confirmation | `LeaseOwnershipModeTransitionsAndLatchedEStop`, HTTP smoke | “AutonomousSim” is a mode label, not autonomous planning permission |
| Stop/cancel/EStop confusion | Separate operations; EStop latched and reset disarmed | HTTP smoke verifies a terminal `cancelled` ROS Action, then injects EStop during another active action and checks safe terminal status plus persisted audit; supervisor GoogleTests | Polling creates a finite reaction delay; not hardware EStop |
| Planner or DB bypasses safety | ROS Action must call C++ authorization service | Sprint 1/2 real-action smoke | ROS network is trusted locally; production isolation absent |

Acceptance fails closed on missing ROS supervisor, stale pose, missing token, missing/expired lease, forbidden mode, missing approval and EStop latch. The control board visibly marks replay as read-only. The active-action EStop drill exercises a real safe terminal outcome; sensor-loss and delayed-feedback drills remain unimplemented. P62/P63 perception and multimodal artifacts are absent, so their compatibility evidence cannot be asserted here.
