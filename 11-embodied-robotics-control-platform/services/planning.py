"""Deterministic, snapshot-bound plans for the simulation's single shoulder joint."""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from typing import Any


class PlanRejected(ValueError):
    """A proposal cannot cross the planning boundary."""


@dataclass(frozen=True)
class TaskNode:
    node_id: str
    action: str
    target_radians: float
    dependencies: tuple[str, ...] = ()
    failure_policy: str = "stop"
    requires_approval: bool = True


@dataclass(frozen=True)
class TaskPlan:
    schema_version: str
    plan_id: str
    run_id: str
    robot_id: str
    snapshot_sequence: int
    snapshot_wall_time_ns: int
    snapshot_hash: str
    snapshot_joint_radians: float
    created_wall_time_ns: int
    source: str
    nodes: tuple[TaskNode, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "nodes": [
                {**asdict(node), "dependencies": list(node.dependencies)} for node in self.nodes
            ],
        }


def observed_shoulder_radians(state: dict[str, Any]) -> float:
    for link in state.get("links", []):
        if link.get("link_name") == "left_arm":
            q = link["orientation"]
            return 2 * math.atan2(float(q["x"]), float(q["w"]))
    raise PlanRejected("left_arm pose missing from observed world state")


def snapshot_hash(state: dict[str, Any]) -> str:
    relevant = {
        "run_id": state["run_id"],
        "robot_id": state["robot_id"],
        "frame_id": state["frame_id"],
        "sequence": state["sequence"],
        "simulation_time_ns": state["simulation_time_ns"],
        "observed_joint_radians": observed_shoulder_radians(state),
    }
    encoded = json.dumps(relevant, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_graph(nodes: tuple[TaskNode, ...]) -> None:
    if not 1 <= len(nodes) <= 4:
        raise PlanRejected("plan must contain one to four nodes")
    ids = [node.node_id for node in nodes]
    if len(set(ids)) != len(ids):
        raise PlanRejected("duplicate node ID")
    seen: set[str] = set()
    for node in nodes:
        if node.action != "move_joint" or node.failure_policy != "stop":
            raise PlanRejected("unknown action or unsafe failure policy")
        if not math.isfinite(node.target_radians) or abs(node.target_radians) > 0.8:
            raise PlanRejected("target outside versioned joint limit")
        if not node.requires_approval:
            raise PlanRejected("every motion node requires operator approval")
        if any(dependency not in seen for dependency in node.dependencies):
            raise PlanRejected("dependency missing, forward or cyclic")
        seen.add(node.node_id)


def propose_plan(
    state: dict[str, Any], *, plan_id: str, target_radians: float, now_ns: int | None = None
) -> TaskPlan:
    now_ns = time.time_ns() if now_ns is None else now_ns
    observed_at = int(state["observed_wall_time_ns"])
    if now_ns < observed_at or now_ns - observed_at > 1_000_000_000:
        raise PlanRejected("world state is stale")
    if state["robot_id"] != "embodied_demo" or state["frame_id"] != "world/studio":
        raise PlanRejected("unsupported robot or frame")
    if not math.isfinite(target_radians) or abs(target_radians) > 0.8:
        raise PlanRejected("target outside versioned joint limit")
    current = observed_shoulder_radians(state)
    if abs(target_radians - current) > 0.8:
        raise PlanRejected("requested displacement exceeds scenario budget")
    nodes = (TaskNode("move-left-shoulder", "move_joint", target_radians),)
    validate_graph(nodes)
    return TaskPlan(
        schema_version="task-plan.v1",
        plan_id=plan_id,
        run_id=state["run_id"],
        robot_id=state["robot_id"],
        snapshot_sequence=int(state["sequence"]),
        snapshot_wall_time_ns=observed_at,
        snapshot_hash=snapshot_hash(state),
        snapshot_joint_radians=current,
        created_wall_time_ns=now_ns,
        source="bounded-deterministic-planner",
        nodes=nodes,
    )


def validate_for_execution(plan: TaskPlan, state: dict[str, Any], now_ns: int) -> None:
    validate_graph(plan.nodes)
    if plan.schema_version != "task-plan.v1" or plan.source != "bounded-deterministic-planner":
        raise PlanRejected("unsupported plan provenance")
    if plan.run_id != state["run_id"] or plan.robot_id != state["robot_id"]:
        raise PlanRejected("plan belongs to a different run or robot")
    if not plan.snapshot_hash or plan.snapshot_sequence < 1:
        raise PlanRejected("plan has no bound snapshot")
    if state["sequence"] < plan.snapshot_sequence:
        raise PlanRejected("world state sequence rewound")
    if state["sequence"] - plan.snapshot_sequence > 5_000:
        raise PlanRejected("plan snapshot is obsolete")
    if now_ns < plan.created_wall_time_ns or now_ns - plan.created_wall_time_ns > 120_000_000_000:
        raise PlanRejected("plan approval window expired")
    if (
        now_ns < state["observed_wall_time_ns"]
        or now_ns - state["observed_wall_time_ns"] > 1_000_000_000
    ):
        raise PlanRejected("current world state is stale")
    if state["frame_id"] != "world/studio":
        raise PlanRejected("invalid world frame")
    current = observed_shoulder_radians(state)
    if not math.isfinite(current) or abs(current - plan.snapshot_joint_radians) > 0.05:
        raise PlanRejected("world state diverged from the plan snapshot")
