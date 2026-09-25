"""Protocol-independent robot state and provenance invariants."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Quaternion:
    x: float
    y: float
    z: float
    w: float


@dataclass(frozen=True)
class LinkPose:
    link_name: str
    position_m: Vector3
    orientation: Quaternion


@dataclass(frozen=True)
class RobotState:
    run_id: str
    robot_id: str
    frame_id: str
    simulation_time_ns: int
    observed_wall_time_ns: int
    sequence: int
    correlation_id: str
    links: tuple[LinkPose, ...]

    def validate(self) -> None:
        if not all((self.run_id, self.robot_id, self.frame_id, self.correlation_id)):
            raise ValueError("identity, frame and correlation are required")
        if self.simulation_time_ns < 0 or self.observed_wall_time_ns <= 0:
            raise ValueError("invalid clocks")
        if self.sequence < 1 or not self.links:
            raise ValueError("sequence and at least one link are required")
        for link in self.links:
            if not link.link_name:
                raise ValueError("unnamed link")
            values = (*vars(link.position_m).values(), *vars(link.orientation).values())
            if not all(math.isfinite(value) for value in values):
                raise ValueError("non-finite pose")
            norm = sum(value * value for value in vars(link.orientation).values())
            if not 0.98 <= norm <= 1.02:
                raise ValueError("orientation must be a unit quaternion")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "schema_version": "robot-state.v1",
            "run_id": self.run_id,
            "robot_id": self.robot_id,
            "frame_id": self.frame_id,
            "clock_domain": "gazebo_sim",
            "simulation_time_ns": self.simulation_time_ns,
            "observed_wall_time_ns": self.observed_wall_time_ns,
            "sequence": self.sequence,
            "source": "gazebo/ros_gz_bridge",
            "correlation_id": self.correlation_id,
            "links": [
                {
                    "link_name": link.link_name,
                    "position_m": vars(link.position_m),
                    "orientation": vars(link.orientation),
                }
                for link in self.links
            ],
        }
