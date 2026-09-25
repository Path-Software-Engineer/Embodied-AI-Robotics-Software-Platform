"""Cross-layer smoke: real ROS Action, independent safety, Gazebo and persisted loop."""

from __future__ import annotations

import json
import time
import urllib.request
import uuid
from pathlib import Path

import rclpy
from action_msgs.msg import GoalStatus
from embodied_interfaces.action import MoveJoint
from embodied_interfaces.srv import ControlAuthority
from rclpy.action import ActionClient


def authority(client, node, run_id: str, lease_id: str, operation: str, mode: str = ""):
    request = ControlAuthority.Request()
    request.operation = operation
    request.run_id = run_id
    request.lease_id = lease_id
    request.actor_id = "sprint1-smoke"
    request.requested_mode = mode
    request.ttl_seconds = 30 if operation == "acquire" else 0
    request.confirmed = operation == "mode"
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5)
    if not future.done() or not future.result().allowed:
        raise RuntimeError(
            f"supervisor rejected {operation}: {future.result() if future.done() else 'timeout'}"
        )
    return future.result()


def goal(
    client: ActionClient,
    node,
    run_id: str,
    target: float,
    sequence: int,
    trace: str,
    lease_id: str,
):
    request = MoveJoint.Goal()
    request.run_id = run_id
    request.robot_id = "embodied_demo"
    request.joint_name = "left_shoulder"
    request.target_radians = target
    request.command_sequence = sequence
    request.correlation_id = trace
    request.lease_id = lease_id
    future = client.send_goal_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=10)
    if not future.done():
        raise RuntimeError("ROS Action goal admission timed out")
    handle = future.result()
    if not handle.accepted:
        return None
    result_future = handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future, timeout_sec=12)
    if not result_future.done():
        raise RuntimeError("ROS Action result timed out")
    return result_future.result()


def api(path: str) -> dict:
    with urllib.request.urlopen(f"http://gateway:8000{path}", timeout=5) as response:
        return json.load(response)


def main() -> None:
    scenario = json.loads(Path("/workspace/sim/scenarios/studio-joint-motion.v1.json").read_text())
    target = scenario["goal"]["target_radians"]
    tolerance = scenario["goal"]["tolerance_radians"]
    run_id = api("/api/v1/robots/embodied_demo/state")["state"]["run_id"]
    if not run_id.startswith(scenario["run_id_prefix"]):
        raise RuntimeError("runtime run ID does not follow the scenario manifest")
    trace = f"sprint1-smoke-{uuid.uuid4().hex[:12]}"
    command_sequence = time.time_ns()
    rclpy.init()
    node = rclpy.create_node("sprint1_action_smoke")
    client = ActionClient(node, MoveJoint, "/simulation/move_joint")
    control = node.create_client(ControlAuthority, "/simulation/control_authority")
    lease_id = f"smoke-{uuid.uuid4().hex}"
    try:
        if not client.wait_for_server(timeout_sec=20):
            raise RuntimeError("ROS Action server unavailable")
        if not control.wait_for_service(timeout_sec=10):
            raise RuntimeError("independent supervisor unavailable")
        authority(control, node, run_id, lease_id, "acquire")
        authority(control, node, run_id, lease_id, "mode", "Manual")
        result = goal(client, node, run_id, target, command_sequence, trace, lease_id)
        if result is None or result.status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError(f"simulated action failed: {result}")
        if not result.result.succeeded or abs(result.result.final_radians - target) > tolerance:
            raise RuntimeError("Gazebo joint feedback did not reach target")
        duplicate = goal(
            client, node, run_id, 0.2, command_sequence, f"{trace}-duplicate", lease_id
        )
        if duplicate is None or duplicate.status != GoalStatus.STATUS_ABORTED:
            raise RuntimeError("duplicate command sequence was not blocked")
        if "duplicate" not in duplicate.result.reason:
            raise RuntimeError("safety supervisor did not explain the duplicate rejection")
        if (
            goal(client, node, run_id, 1.1, command_sequence + 1, f"{trace}-unsafe", lease_id)
            is not None
        ):
            raise RuntimeError("out-of-range target was admitted")

        events = []
        for _ in range(30):
            payload = api(f"/api/v1/simulation-runs/{run_id}/loop-events?limit=200")
            events = [event for event in payload["events"] if event["correlation_id"] == trace]
            if events and events[-1]["status"] == "completed":
                break
            time.sleep(0.2)
        expected = {"perception", "state", "memory", "intent", "safety", "action", "feedback"}
        if {event["stage"] for event in events} != expected:
            raise RuntimeError(f"persisted loop stages incomplete: {events}")
        if not payload["read_only"]:
            raise RuntimeError("loop replay is not read-only")
        live_before_replay = api("/api/v1/robots/embodied_demo/state")["state"]
        runs = api("/api/v1/simulation-runs?limit=20")
        if not runs["read_only"] or run_id not in {run["run_id"] for run in runs["runs"]}:
            raise RuntimeError("persisted run is not discoverable for replay")
        samples = api(f"/api/v1/simulation-runs/{run_id}/samples?limit=5")
        if not samples["read_only"] or not samples["samples"]:
            raise RuntimeError("pose replay is empty or writable")
        state = api("/api/v1/robots/embodied_demo/state")
        if state["stale"] or len(state["state"]["links"]) != 3:
            raise RuntimeError("live Gazebo state is stale or missing links")
        if state["state"]["run_id"] != live_before_replay["run_id"]:
            raise RuntimeError("replay changed the live simulation run")
        if state["state"]["sequence"] < live_before_replay["sequence"]:
            raise RuntimeError("replay rewound the live simulation sequence")
        print(
            json.dumps(
                {
                    "status": "passed",
                    "trace": trace,
                    "run_id": run_id,
                    "stages": len(expected),
                    "events": len(events),
                    "final_radians": result.result.final_radians,
                    "duplicate_rejected": True,
                    "out_of_range_rejected": True,
                    "persisted_pose_samples": len(samples["samples"]),
                }
            )
        )
    finally:
        if control.service_is_ready():
            try:
                authority(control, node, run_id, lease_id, "revoke")
            except RuntimeError:
                pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
