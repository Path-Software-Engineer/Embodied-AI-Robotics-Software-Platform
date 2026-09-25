import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from services.domain import LinkPose, Quaternion, RobotState, Vector3
from services.gateway import StateHub, app, as_loop_event, as_state
from services.generated import robot_state_pb2


def valid_state(sequence: int = 1) -> RobotState:
    return RobotState(
        run_id="test-run",
        robot_id="embodied_demo",
        frame_id="world/studio",
        simulation_time_ns=100,
        observed_wall_time_ns=1_000_000_000,
        sequence=sequence,
        correlation_id="test-trace",
        links=(LinkPose("torso", Vector3(0.0, 0.0, 1.0), Quaternion(0, 0, 0, 1)),),
    )


def test_domain_state_validates_against_public_schema() -> None:
    schema = Path("contracts/schemas/robot-state.v1.schema.json")
    jsonschema.validate(valid_state().to_dict(), json.loads(schema.read_text()))


def test_invalid_pose_and_missing_identity_are_rejected() -> None:
    with pytest.raises(ValueError, match="orientation"):
        RobotState(
            **{
                **vars(valid_state()),
                "links": (LinkPose("torso", Vector3(0, 0, 1), Quaternion(0, 0, 0, 2)),),
            }
        ).validate()
    with pytest.raises(ValueError, match="identity"):
        RobotState(**{**vars(valid_state()), "frame_id": ""}).validate()


def test_gateway_rejects_wrong_version_and_sequence_replay() -> None:
    bad = robot_state_pb2.RobotState(schema_version="unknown", sequence=1)
    with pytest.raises(ValueError, match="contract"):
        as_state(bad)
    hub = StateHub()
    hub.publish(valid_state().to_dict())
    with pytest.raises(ValueError, match="duplicate"):
        hub.publish(valid_state().to_dict())
    hub.publish(valid_state(sequence=2).to_dict())
    assert hub.latest is not None and hub.latest["sequence"] == 2


def test_live_client_queue_remains_bounded() -> None:
    import asyncio

    hub = StateHub()
    queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=2)
    hub.clients.add(queue)
    for sequence in range(1, 5):
        hub.publish(valid_state(sequence).to_dict())
    assert queue.qsize() == 2
    assert queue.get_nowait()["sequence"] == 3


def test_loop_event_requires_versioned_real_action_provenance() -> None:
    event = robot_state_pb2.LoopEvent(
        schema_version="embodied-loop-event.v1",
        run_id="test-run",
        robot_id="embodied_demo",
        correlation_id="action-1",
        clock_domain="gazebo_sim",
        simulation_time_ns=500_000_000,
        stage="feedback",
        status="completed",
        event_sequence=7,
        observed_wall_time_ns=1_000_000_000,
        observed_joint_radians=0.45,
        target_joint_radians=0.5,
        detail="observed joint reached target",
    )
    normalized = as_loop_event(event)
    schema = json.loads(Path("contracts/schemas/loop-event.v1.schema.json").read_text())
    jsonschema.validate(normalized, schema)
    assert normalized["target_joint_radians"] == 0.5
    assert normalized["correlation_id"] == "action-1"
    event.stage = "fictional"
    with pytest.raises(ValueError, match="stage"):
        as_loop_event(event)


def test_loop_fanout_and_memory_are_bounded() -> None:
    import asyncio

    hub = StateHub()
    queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=2)
    hub.loop_clients.add(queue)
    for sequence in range(300):
        hub.publish_loop({"event_sequence": sequence})
    assert len(hub.loop_events) == 256
    assert hub.loop_write_queue.qsize() == 256
    assert [queue.get_nowait()["event_sequence"] for _ in range(2)] == [298, 299]


def test_scenario_schema_and_asset_digests_are_exact() -> None:
    scenario = json.loads(Path("sim/scenarios/studio-joint-motion.v1.json").read_text())
    schema = json.loads(Path("contracts/schemas/scenario.v1.schema.json").read_text())
    jsonschema.validate(scenario, schema)
    manifest = json.loads(Path("sim/assets/manifest.v1.json").read_text())
    assert manifest["schema_version"] == "embodied-asset-manifest.v1"
    assert len(manifest["assets"]) == 3
    for asset in manifest["assets"]:
        digest = hashlib.sha256(Path(asset["path"]).read_bytes()).hexdigest()
        assert digest == asset["sha256"]
    for name in ("RobotState.msg", "LoopEvent.msg"):
        assert (
            Path(f"contracts/ros/msg/{name}").read_bytes()
            == Path(f"ros_ws/src/embodied_interfaces/msg/{name}").read_bytes()
        )


def test_websocket_channels_are_observation_only() -> None:
    contract = json.loads(Path("contracts/websocket/asyncapi.json").read_text())
    assert contract["asyncapi"] == "3.0.0"
    assert set(contract["channels"]) == {"robotState", "loopEvents"}
    assert all(operation["action"] == "receive" for operation in contract["operations"].values())


def test_sprint_two_ros_contract_mirrors_and_http_surface() -> None:
    for kind, names in {
        "srv": ("AuthorizeMotion.srv", "ControlAuthority.srv"),
        "action": ("MoveJoint.action",),
    }.items():
        for name in names:
            assert (
                Path(f"contracts/ros/{kind}/{name}").read_bytes()
                == Path(f"ros_ws/src/embodied_interfaces/{kind}/{name}").read_bytes()
            )
    spec = app.openapi()
    assert spec["info"]["version"] == "0.2.0"
    assert "/api/v2/control/leases" in spec["paths"]
    assert "/api/v2/plans/{plan_id}/execute" in spec["paths"]
    assert "post" not in spec["paths"]["/api/v1/simulation-runs/{run_id}/samples"]


def test_python_runtime_lock_covers_direct_dependencies() -> None:
    def pinned(path: str) -> set[str]:
        return {
            line.strip().lower()
            for line in Path(path).read_text().splitlines()
            if line.strip() and not line.startswith("#")
        }

    direct = pinned("services/requirements.txt")
    lock = pinned("services/requirements.lock")
    assert direct <= lock
    assert all(line.count("==") == 1 for line in lock)
