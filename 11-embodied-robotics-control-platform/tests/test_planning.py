import copy
import json
import time
from pathlib import Path

import jsonschema
import pytest

from services.planning import (
    PlanRejected,
    TaskNode,
    propose_plan,
    snapshot_hash,
    validate_for_execution,
    validate_graph,
)


def state(now_ns: int) -> dict:
    return {
        "run_id": "studio-test",
        "robot_id": "embodied_demo",
        "frame_id": "world/studio",
        "sequence": 10,
        "simulation_time_ns": 2_000_000_000,
        "observed_wall_time_ns": now_ns - 100_000_000,
        "links": [{"link_name": "left_arm", "orientation": {"x": 0.0, "w": 1.0}}],
    }


def test_deterministic_bounded_plan_binds_to_real_snapshot() -> None:
    now = time.time_ns()
    observed = state(now)
    plan = propose_plan(observed, plan_id="plan-1", target_radians=0.4, now_ns=now)
    assert plan.snapshot_hash == snapshot_hash(observed)
    assert plan.nodes[0].requires_approval
    assert plan.to_dict()["schema_version"] == "task-plan.v1"
    schema = json.loads(Path("contracts/schemas/task-plan.v1.schema.json").read_text())
    jsonschema.validate(plan.to_dict(), schema)
    validate_for_execution(plan, observed, now + 100_000_000)


@pytest.mark.parametrize("target", [0.81, float("nan"), float("inf")])
def test_unsafe_proposals_fail(target: float) -> None:
    now = time.time_ns()
    with pytest.raises(PlanRejected, match="limit"):
        propose_plan(state(now), plan_id="bad", target_radians=target, now_ns=now)


def test_stale_cross_run_and_obsolete_plans_fail_closed() -> None:
    now = time.time_ns()
    observed = state(now)
    plan = propose_plan(observed, plan_id="plan-1", target_radians=0.2, now_ns=now)
    with pytest.raises(PlanRejected, match="expired"):
        validate_for_execution(plan, observed, now + 121_000_000_000)
    changed = copy.deepcopy(observed)
    changed["run_id"] = "other-run"
    with pytest.raises(PlanRejected, match="different run"):
        validate_for_execution(plan, changed, now)
    changed = copy.deepcopy(observed)
    changed["sequence"] = 5_100
    with pytest.raises(PlanRejected, match="obsolete"):
        validate_for_execution(plan, changed, now)


def test_dependency_cycle_and_no_approval_are_rejected() -> None:
    with pytest.raises(PlanRejected, match="dependency"):
        validate_graph((TaskNode("a", "move_joint", 0.1, ("b",)), TaskNode("b", "move_joint", 0.2)))
    with pytest.raises(PlanRejected, match="approval"):
        validate_graph((TaskNode("a", "move_joint", 0.1, requires_approval=False),))


def test_pose_drift_stale_sensor_and_rewound_sequence_reject_execution() -> None:
    now = time.time_ns()
    observed = state(now)
    plan = propose_plan(observed, plan_id="plan-1", target_radians=0.2, now_ns=now)
    drifted = copy.deepcopy(observed)
    drifted["links"][0]["orientation"]["x"] = 0.1
    with pytest.raises(PlanRejected, match="diverged"):
        validate_for_execution(plan, drifted, now)
    stale = copy.deepcopy(observed)
    stale["observed_wall_time_ns"] = now - 2_000_000_000
    with pytest.raises(PlanRejected, match="stale"):
        validate_for_execution(plan, stale, now)
    rewound = copy.deepcopy(observed)
    rewound["sequence"] = 9
    with pytest.raises(PlanRejected, match="rewound"):
        validate_for_execution(plan, rewound, now)


def test_future_plan_timestamp_and_wrong_frame_reject_execution() -> None:
    now = time.time_ns()
    observed = state(now)
    plan = propose_plan(observed, plan_id="plan-1", target_radians=0.2, now_ns=now)
    with pytest.raises(PlanRejected, match="expired"):
        validate_for_execution(plan, observed, now - 1)
    wrong_frame = copy.deepcopy(observed)
    wrong_frame["frame_id"] = "robot/local"
    with pytest.raises(PlanRejected, match="frame"):
        validate_for_execution(plan, wrong_frame, now)
