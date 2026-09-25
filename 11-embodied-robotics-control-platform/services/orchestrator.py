"""ROS state subscriber and gRPC server. No synthetic pose fallback exists."""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import grpc
import rclpy
from embodied_interfaces.msg import LoopEvent as RosLoopEvent
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from tf2_msgs.msg import TFMessage

from services.domain import LinkPose, Quaternion, RobotState, Vector3
from services.generated import robot_state_pb2, robot_state_pb2_grpc


def to_proto(state: RobotState) -> robot_state_pb2.RobotState:
    state.validate()
    result = robot_state_pb2.RobotState(
        schema_version="robot-state.v1",
        run_id=state.run_id,
        robot_id=state.robot_id,
        frame_id=state.frame_id,
        clock_domain="gazebo_sim",
        simulation_time_ns=state.simulation_time_ns,
        observed_wall_time_ns=state.observed_wall_time_ns,
        sequence=state.sequence,
        source="gazebo/ros_gz_bridge",
        correlation_id=state.correlation_id,
    )
    for link in state.links:
        target = result.links.add(link_name=link.link_name)
        target.position_m.x = link.position_m.x
        target.position_m.y = link.position_m.y
        target.position_m.z = link.position_m.z
        target.orientation.x = link.orientation.x
        target.orientation.y = link.orientation.y
        target.orientation.z = link.orientation.z
        target.orientation.w = link.orientation.w
    return result


class StateNode(Node):
    def __init__(self) -> None:
        super().__init__("embodied_state_orchestrator")
        self.run_id = os.environ.get("RUN_ID", "studio-local")
        self.robot_id = "embodied_demo"
        self._clock_ns: int | None = None
        self._sequence = 0
        self._state: RobotState | None = None
        self.condition = threading.Condition()
        self.loop_condition = threading.Condition()
        self.loop_events: deque[robot_state_pb2.LoopEvent] = deque(maxlen=256)
        self.create_subscription(Clock, "/clock", self._on_clock, 10)
        self.create_subscription(TFMessage, "/model/embodied_demo/pose", self._on_pose, 10)
        self.create_subscription(RosLoopEvent, "/simulation/loop_events", self._on_loop_event, 20)

    def _on_loop_event(self, event: RosLoopEvent) -> None:
        if event.schema_version != "embodied-loop-event.v1" or event.run_id != self.run_id:
            return
        record = robot_state_pb2.LoopEvent(
            schema_version=event.schema_version,
            run_id=event.run_id,
            robot_id=event.robot_id,
            correlation_id=event.correlation_id,
            clock_domain=event.clock_domain,
            simulation_time_ns=event.simulation_time_ns,
            stage=event.stage,
            status=event.status,
            event_sequence=event.event_sequence,
            observed_wall_time_ns=event.observed_wall_time_ns,
            observed_joint_radians=event.observed_joint_radians,
            target_joint_radians=event.target_joint_radians,
            detail=event.detail,
        )
        with self.loop_condition:
            self.loop_events.append(record)
            self.loop_condition.notify_all()

    def _on_clock(self, message: Clock) -> None:
        self._clock_ns = message.clock.sec * 1_000_000_000 + message.clock.nanosec

    def _on_pose(self, message: TFMessage) -> None:
        if self._clock_ns is None:
            return
        links: list[LinkPose] = []
        for transform in message.transforms:
            name = transform.child_frame_id.replace("::", "/").split("/")[-1]
            if name not in {"torso", "head", "left_arm"}:
                continue
            point = transform.transform.translation
            rotation = transform.transform.rotation
            links.append(
                LinkPose(
                    name,
                    Vector3(point.x, point.y, point.z),
                    Quaternion(rotation.x, rotation.y, rotation.z, rotation.w),
                )
            )
        if not links:
            return
        self._sequence += 1
        state = RobotState(
            run_id=self.run_id,
            robot_id=self.robot_id,
            frame_id="world/studio",
            simulation_time_ns=self._clock_ns,
            observed_wall_time_ns=time.time_ns(),
            sequence=self._sequence,
            correlation_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.run_id}:{self._sequence}")),
            links=tuple(links),
        )
        try:
            state.validate()
        except ValueError as error:
            self.get_logger().error(f"invalid Gazebo pose rejected: {error}")
            return
        with self.condition:
            self._state = state
            self.condition.notify_all()

    def latest(self) -> RobotState | None:
        with self.condition:
            return self._state


class RobotStateService(robot_state_pb2_grpc.RobotStateServiceServicer):
    def __init__(self, node: StateNode) -> None:
        self.node = node

    def Latest(self, _request, context):  # noqa: N802
        state = self.node.latest()
        if state is None:
            context.abort(grpc.StatusCode.UNAVAILABLE, "waiting for ROS clock and pose")
        return to_proto(state)

    def Watch(self, _request, context):  # noqa: N802
        last_sequence = 0
        while context.is_active():
            with self.node.condition:
                self.node.condition.wait_for(
                    lambda seen=last_sequence: self.node._state is not None
                    and self.node._state.sequence > seen,
                    timeout=1.0,
                )
                state = self.node._state
            if state is not None and state.sequence > last_sequence:
                last_sequence = state.sequence
                yield to_proto(state)

    def WatchLoop(self, _request, context):  # noqa: N802
        last_sequence = 0
        while context.is_active():
            with self.node.loop_condition:
                self.node.loop_condition.wait_for(
                    lambda seen=last_sequence: bool(self.node.loop_events)
                    and self.node.loop_events[-1].event_sequence > seen,
                    timeout=1.0,
                )
                events = [
                    event for event in self.node.loop_events if event.event_sequence > last_sequence
                ]
            for event in events:
                last_sequence = event.event_sequence
                yield event


def main() -> None:
    rclpy.init()
    node = StateNode()
    server = grpc.server(ThreadPoolExecutor(max_workers=8))
    robot_state_pb2_grpc.add_RobotStateServiceServicer_to_server(RobotStateService(node), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    try:
        rclpy.spin(node)
    finally:
        server.stop(grace=1)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
