"""ROS state subscriber and gRPC server. No synthetic pose fallback exists."""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import grpc
import rclpy
from action_msgs.msg import GoalStatus
from embodied_interfaces.action import MoveJoint
from embodied_interfaces.msg import LoopEvent as RosLoopEvent
from embodied_interfaces.srv import ControlAuthority
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from tf2_msgs.msg import TFMessage

from services.domain import LinkPose, Quaternion, RobotState, Vector3
from services.generated import robot_state_pb2, robot_state_pb2_grpc
from services.planning import PlanRejected, propose_plan


def wait_ros(future, timeout_s: float):
    deadline = time.monotonic() + timeout_s
    while not future.done() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not future.done():
        raise TimeoutError("ROS operation timed out")
    return future.result()


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
        self.control_group = ReentrantCallbackGroup()
        self.authority_client = self.create_client(
            ControlAuthority, "/simulation/control_authority", callback_group=self.control_group
        )
        self.action_client = ActionClient(
            self, MoveJoint, "/simulation/move_joint", callback_group=self.control_group
        )
        self.action_lock = threading.Lock()
        self.active_trace: str | None = None
        self.active_lease: str | None = None
        self.active_handle = None
        self.pending_cancel = False
        self.last_command_sequence = 0
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


class ControlService(robot_state_pb2_grpc.ControlServiceServicer):
    def __init__(self, node: StateNode) -> None:
        self.node = node

    def Authority(self, request, context):  # noqa: N802
        if request.run_id != self.node.run_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "wrong simulation run")
        if not self.node.authority_client.wait_for_service(timeout_sec=1):
            context.abort(grpc.StatusCode.UNAVAILABLE, "safety supervisor unavailable")
        ros = ControlAuthority.Request()
        ros.operation = request.operation
        ros.run_id = request.run_id
        ros.lease_id = request.lease_id
        ros.actor_id = request.actor_id
        ros.requested_mode = request.requested_mode
        ros.ttl_seconds = request.ttl_seconds
        ros.confirmed = request.confirmed
        ros.reason = request.reason
        try:
            result = wait_ros(self.node.authority_client.call_async(ros), 2)
        except TimeoutError:
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "supervisor did not answer")
        if result.allowed and request.operation in {"stop", "estop", "revoke"}:
            with self.node.action_lock:
                handle = self.node.active_handle
                if self.node.active_trace is not None and handle is None:
                    self.node.pending_cancel = True
            if handle is not None:
                handle.cancel_goal_async()
        return robot_state_pb2.ControlReply(
            allowed=result.allowed,
            mode=result.mode,
            estop_latched=result.estop_latched,
            lease_id=result.lease_id,
            lease_matches=result.lease_matches,
            lease_owner=result.lease_owner,
            expires_at_wall_ms=result.expires_at_wall_ms,
            reason=result.reason,
        )

    def Plan(self, request, context):  # noqa: N802
        state = self.node.latest()
        if state is None or state.run_id != request.run_id:
            context.abort(grpc.StatusCode.UNAVAILABLE, "matching world state unavailable")
        try:
            plan = propose_plan(
                state.to_dict(), plan_id=request.plan_id, target_radians=request.target_radians
            )
        except PlanRejected as error:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(error))
        return robot_state_pb2.PlanReply(plan_json=json.dumps(plan.to_dict(), sort_keys=True))

    def Execute(self, request, context):  # noqa: N802
        if request.run_id != self.node.run_id or not all(
            (request.plan_id, request.lease_id, request.correlation_id, request.actor_id)
        ):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "missing execution provenance")
        if not self.node.action_client.wait_for_server(timeout_sec=2):
            context.abort(grpc.StatusCode.UNAVAILABLE, "ROS Action unavailable")
        with self.node.action_lock:
            if self.node.active_trace is not None:
                context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "another task is active")
            sequence = max(time.time_ns(), self.node.last_command_sequence + 1)
            self.node.last_command_sequence = sequence
            self.node.active_trace = request.correlation_id
            self.node.active_lease = request.lease_id
            self.node.pending_cancel = False
        try:
            goal = MoveJoint.Goal()
            goal.run_id = request.run_id
            goal.robot_id = "embodied_demo"
            goal.joint_name = "left_shoulder"
            goal.target_radians = request.target_radians
            goal.command_sequence = sequence
            goal.correlation_id = request.correlation_id
            goal.lease_id = request.lease_id
            handle = wait_ros(self.node.action_client.send_goal_async(goal), 3)
            if not handle.accepted:
                return robot_state_pb2.ExecuteReply(
                    accepted=False, reason="ROS Action rejected goal", command_sequence=sequence
                )
            with self.node.action_lock:
                self.node.active_handle = handle
                cancel_pending = self.node.pending_cancel
            if cancel_pending:
                handle.cancel_goal_async()
            outcome = wait_ros(handle.get_result_async(), 12)
            return robot_state_pb2.ExecuteReply(
                accepted=True,
                succeeded=outcome.status == GoalStatus.STATUS_SUCCEEDED
                and outcome.result.succeeded,
                canceled=outcome.status == GoalStatus.STATUS_CANCELED,
                reason=outcome.result.reason,
                final_radians=outcome.result.final_radians,
                command_sequence=sequence,
            )
        except TimeoutError:
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "action result timed out")
        finally:
            with self.node.action_lock:
                self.node.active_handle = None
                self.node.active_trace = None
                self.node.active_lease = None
                self.node.pending_cancel = False

    def Cancel(self, request, context):  # noqa: N802
        if request.run_id != self.node.run_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "wrong simulation run")
        with self.node.action_lock:
            handle = self.node.active_handle
            matches = (
                request.correlation_id == self.node.active_trace
                and request.lease_id == self.node.active_lease
            )
            if matches and handle is None:
                self.node.pending_cancel = True
        if not matches:
            return robot_state_pb2.CancelReply(accepted=False, reason="no matching active action")
        if handle is None:
            return robot_state_pb2.CancelReply(
                accepted=True, reason="cancel queued until ROS goal acknowledgement"
            )
        try:
            result = wait_ros(handle.cancel_goal_async(), 2)
        except TimeoutError:
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "cancel acknowledgement timed out")
        return robot_state_pb2.CancelReply(
            accepted=bool(result.goals_canceling),
            reason="cancel requested" if result.goals_canceling else "action already terminal",
        )


def main() -> None:
    rclpy.init()
    node = StateNode()
    server = grpc.server(ThreadPoolExecutor(max_workers=8))
    robot_state_pb2_grpc.add_RobotStateServiceServicer_to_server(RobotStateService(node), server)
    robot_state_pb2_grpc.add_ControlServiceServicer_to_server(ControlService(node), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    try:
        executor = MultiThreadedExecutor(num_threads=4)
        executor.add_node(node)
        executor.spin()
    finally:
        server.stop(grace=1)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
