"""Real HTTP → gRPC → ROS Action/Safety → Gazebo → Timescale acceptance."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "http://127.0.0.1:8000"
ACTOR = "sprint2-smoke"


def request(
    path: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    lease: str = "",
    token: str | None = None,
) -> tuple[int, dict]:
    encoded = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json", "X-Actor-Id": ACTOR}
    if method != "GET":
        headers["Authorization"] = f"Bearer {token or os.environ['EMBODIED_OPERATOR_TOKEN']}"
    if lease:
        headers["X-Control-Lease"] = lease
    operation = urllib.request.Request(BASE + path, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(operation, timeout=25) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"detail": raw[:300] or "non-JSON server error"}
        return error.code, payload


def expect(code: int, payload: dict, expected: int) -> dict:
    if code != expected:
        raise RuntimeError(f"expected HTTP {expected}, received {code}: {payload}")
    return payload


def main() -> None:
    if len(os.environ.get("EMBODIED_OPERATOR_TOKEN", "")) < 32:
        raise RuntimeError("EMBODIED_OPERATOR_TOKEN required for the control smoke")
    status = expect(*request("/api/v2/control/status"), 200)
    run_id = status["run_id"]
    if status["mode"] != "Disarmed" or status["estop_latched"]:
        raise RuntimeError("supervisor did not start disarmed")
    expect(*request("/api/v2/control/leases", method="POST", body={}, token="invalid"), 401)
    lease = expect(*request("/api/v2/control/leases", method="POST", body={}), 200)["lease_id"]
    expect(*request("/api/v2/control/leases", method="POST", body={}), 409)
    expect(
        *request(
            "/api/v2/control/mode",
            method="POST",
            lease=lease,
            body={
                "requested_mode": "AutonomousSim",
                "confirmed": True,
                "reason": "forbidden direct transition",
            },
        ),
        409,
    )
    expect(
        *request(
            "/api/v2/control/mode",
            method="POST",
            lease=lease,
            body={
                "requested_mode": "Manual",
                "confirmed": True,
                "reason": "bounded simulation smoke",
            },
        ),
        200,
    )
    plan = expect(*request("/api/v2/plans", method="POST", body={"target_radians": 0.15}), 200)[
        "plan"
    ]
    plan_id = plan["plan_id"]
    if plan["run_id"] != run_id or not plan["snapshot_hash"]:
        raise RuntimeError("plan is not bound to the live simulation snapshot")
    expect(*request(f"/api/v2/plans/{plan_id}/execute", method="POST", lease=lease), 409)
    expect(
        *request(
            f"/api/v2/plans/{plan_id}/approve",
            method="POST",
            lease=lease,
            body={"confirmed": True, "reason": "operator reviewed bounded joint move"},
        ),
        200,
    )
    outcome = expect(*request(f"/api/v2/plans/{plan_id}/execute", method="POST", lease=lease), 200)
    if outcome["status"] != "completed" or abs(outcome["final_radians"] - 0.15) > 0.05:
        raise RuntimeError(f"ROS/Gazebo action did not reach expected target: {outcome}")
    events = expect(*request(f"/api/v2/simulation-runs/{run_id}/control-events"), 200)
    observed = {event["status"] for event in events["events"] if event["plan_id"] == plan_id}
    if not {"proposed", "approved", "running", "completed"} <= observed:
        raise RuntimeError(f"mission audit is incomplete: {observed}")
    cancel_plan = expect(
        *request("/api/v2/plans", method="POST", body={"target_radians": -0.55}), 200
    )["plan"]
    cancel_plan_id = cancel_plan["plan_id"]
    expect(
        *request(
            f"/api/v2/plans/{cancel_plan_id}/approve",
            method="POST",
            lease=lease,
            body={"confirmed": True, "reason": "test terminal ROS cancellation"},
        ),
        200,
    )
    with ThreadPoolExecutor(max_workers=1) as executor:
        execution = executor.submit(
            request, f"/api/v2/plans/{cancel_plan_id}/execute", method="POST", lease=lease
        )
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if execution.done():
                raise RuntimeError("action finished before cancellation could be tested")
            running = expect(*request(f"/api/v2/plans/{cancel_plan_id}"), 200)
            if running["status"] == "running":
                break
            time.sleep(0.02)
        else:
            raise RuntimeError("cancel action never entered running state")
        cancel = expect(
            *request(f"/api/v2/plans/{cancel_plan_id}/cancel", method="POST", lease=lease), 200
        )
        if not cancel["accepted"]:
            raise RuntimeError(f"ROS Action cancellation was not acknowledged: {cancel}")
        cancel_outcome = expect(*execution.result(timeout=20), 200)
    if cancel_outcome["status"] != "cancelled":
        raise RuntimeError(f"cancel did not produce a terminal cancelled action: {cancel_outcome}")
    fault_plan = expect(
        *request("/api/v2/plans", method="POST", body={"target_radians": -0.55}), 200
    )["plan"]
    fault_plan_id = fault_plan["plan_id"]
    expect(
        *request(
            f"/api/v2/plans/{fault_plan_id}/approve",
            method="POST",
            lease=lease,
            body={"confirmed": True, "reason": "controlled EStop injection rehearsal"},
        ),
        200,
    )
    with ThreadPoolExecutor(max_workers=1) as executor:
        execution = executor.submit(
            request, f"/api/v2/plans/{fault_plan_id}/execute", method="POST", lease=lease
        )
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if execution.done():
                raise RuntimeError("fault action finished before EStop could be injected")
            running = expect(*request(f"/api/v2/plans/{fault_plan_id}"), 200)
            if running["status"] == "running":
                break
            time.sleep(0.02)
        else:
            raise RuntimeError("fault action never entered running state")
        estop = expect(
            *request(
                "/api/v2/control/estop",
                method="POST",
                body={"confirmed": True, "reason": "inject EStop during active ROS Action"},
            ),
            200,
        )
        fault_outcome = expect(*execution.result(timeout=20), 200)
    if fault_outcome["status"] not in {"cancelled", "failed"}:
        raise RuntimeError(f"EStop did not terminate the active action: {fault_outcome}")
    fault_events = expect(*request(f"/api/v2/simulation-runs/{run_id}/control-events"), 200)
    fault_statuses = {
        event["status"] for event in fault_events["events"] if event["plan_id"] == fault_plan_id
    }
    if fault_outcome["status"] not in fault_statuses:
        raise RuntimeError("fault terminal outcome was not persisted in mission audit")
    if not estop["estop_latched"] or estop["mode"] != "Disarmed":
        raise RuntimeError("EStop did not latch and disarm")
    expect(*request("/api/v2/control/leases", method="POST", body={}), 409)
    reset = expect(
        *request(
            "/api/v2/control/reset_estop",
            method="POST",
            body={"confirmed": True, "reason": "explicit local reset drill"},
        ),
        200,
    )
    if reset["estop_latched"] or reset["mode"] != "Disarmed":
        raise RuntimeError("EStop reset rearmed the robot unexpectedly")
    print(
        json.dumps(
            {
                "status": "passed",
                "run_id": run_id,
                "plan_id": plan_id,
                "final_radians": outcome["final_radians"],
                "audited_statuses": sorted(observed),
                "exclusive_lease": True,
                "forbidden_transition": True,
                "cancel_terminal": cancel_outcome["status"],
                "latched_estop": True,
                "fault_injection": {
                    "type": "estop_during_action",
                    "plan_id": fault_plan_id,
                    "terminal_status": fault_outcome["status"],
                },
            }
        )
    )


if __name__ == "__main__":
    main()
