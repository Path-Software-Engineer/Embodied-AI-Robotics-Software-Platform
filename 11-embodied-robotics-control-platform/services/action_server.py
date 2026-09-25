"""ROS Action adapter for one bounded, simulation-only shoulder movement."""

from __future__ import annotations

import math
import os
import time
from collections import deque

import rclpy
from embodied_interfaces.action import MoveJoint
from embodied_interfaces.msg import LoopEvent
from embodied_interfaces.srv import AuthorizeMotion, ControlAuthority
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Float64
from tf2_msgs.msg import TFMessage


class SimulationActionServer(Node):
    def __init__(self) -> None:
        super().__init__("simulation_action_adapter")
        self.run_id = os.environ.get("RUN_ID", "studio-local")
        self.latest_angle: float | None = None
        self.last_pose_wall_ns = 0
        self.last_sim_time_ns = 0
        self.memory: deque[tuple[int, float]] = deque(maxlen=32)
        self.event_sequence = 0
        self.group = ReentrantCallbackGroup()
        self.create_subscription(
            TFMessage,
            "/model/embodied_demo/pose",
            self.on_pose,
            10,
            callback_group=self.group,
        )
        self.publisher = self.create_publisher(
            Float64, "/model/embodied_demo/left_shoulder/cmd_pos", 10
        )
        self.events = self.create_publisher(LoopEvent, "/simulation/loop_events", 20)
        self.safety = self.create_client(
            AuthorizeMotion, "/simulation/authorize_motion", callback_group=self.group
        )
        self.control = self.create_client(
            ControlAuthority, "/simulation/control_authority", callback_group=self.group
        )
        self.server = ActionServer(
            self,
            MoveJoint,
            "/simulation/move_joint",
            self.execute,
            goal_callback=self.accept_goal,
            cancel_callback=self.cancel_goal,
            callback_group=self.group,
        )

    def on_pose(self, message: TFMessage) -> None:
        for transform in message.transforms:
            if transform.child_frame_id.endswith("/left_arm"):
                q = transform.transform.rotation
                self.latest_angle = 2 * math.atan2(q.x, q.w)
                self.last_pose_wall_ns = time.time_ns()
                self.last_sim_time_ns = (
                    transform.header.stamp.sec * 1_000_000_000 + transform.header.stamp.nanosec
                )
                self.memory.append((self.last_pose_wall_ns, self.latest_angle))
                return

    def emit(self, goal: MoveJoint.Goal, stage: str, status: str, detail: str) -> None:
        self.event_sequence += 1
        event = LoopEvent()
        event.schema_version = "embodied-loop-event.v1"
        event.run_id = goal.run_id
        event.robot_id = goal.robot_id
        event.correlation_id = goal.correlation_id
        event.clock_domain = "gazebo_sim"
        event.simulation_time_ns = self.last_sim_time_ns
        event.stage = stage
        event.status = status
        event.event_sequence = self.event_sequence
        event.observed_wall_time_ns = time.time_ns()
        event.observed_joint_radians = self.latest_angle or 0.0
        event.target_joint_radians = goal.target_radians
        event.detail = detail
        self.events.publish(event)

    def accept_goal(self, request: MoveJoint.Goal) -> GoalResponse:
        valid = (
            request.run_id == self.run_id
            and request.robot_id == "embodied_demo"
            and request.joint_name == "left_shoulder"
            and bool(request.correlation_id)
            and bool(request.lease_id)
            and request.command_sequence > 0
            and math.isfinite(request.target_radians)
            and abs(request.target_radians) <= 0.8
        )
        return GoalResponse.ACCEPT if valid else GoalResponse.REJECT

    def cancel_goal(self, _goal_handle) -> CancelResponse:
        return CancelResponse.ACCEPT

    def execute(self, goal_handle) -> MoveJoint.Result:
        result = MoveJoint.Result()
        goal = goal_handle.request
        if self.latest_angle is None or time.time_ns() - self.last_pose_wall_ns > 1_000_000_000:
            goal_handle.abort()
            result.reason = "pose unavailable or stale"
            self.emit(goal, "perception", "rejected", result.reason)
            return result
        self.emit(goal, "perception", "observed", "left_arm pose received through ROS TF")
        self.emit(goal, "state", "estimated", "joint angle and freshness validated")
        self.emit(goal, "memory", "bounded", f"{len(self.memory)} recent pose observations")
        self.emit(goal, "intent", "proposed", "typed shoulder target; not yet dispatched")
        if not self.safety.wait_for_service(timeout_sec=2):
            goal_handle.abort()
            result.reason = "independent safety supervisor unavailable"
            self.emit(goal, "safety", "rejected", result.reason)
            return result
        authorization = AuthorizeMotion.Request()
        authorization.run_id = goal.run_id
        authorization.robot_id = goal.robot_id
        authorization.joint_name = goal.joint_name
        authorization.target_radians = goal.target_radians
        authorization.command_sequence = goal.command_sequence
        authorization.correlation_id = goal.correlation_id
        authorization.lease_id = goal.lease_id
        future = self.safety.call_async(authorization)
        deadline = time.monotonic() + 2
        while not future.done() and time.monotonic() < deadline:
            time.sleep(0.02)
        if not future.done() or not future.result().allowed:
            goal_handle.abort()
            result.reason = (
                "safety authorization timed out" if not future.done() else future.result().reason
            )
            self.emit(goal, "safety", "rejected", result.reason)
            return result
        self.emit(goal, "safety", "authorized", future.result().reason)
        command = Float64()
        deadline = time.monotonic() + 8
        feedback_count = 0
        last_authority_check = 0.0
        dispatched = False
        while time.monotonic() < deadline:
            if goal_handle.is_cancel_requested:
                if self.latest_angle is not None:
                    command.data = self.latest_angle
                    self.publisher.publish(command)
                goal_handle.canceled()
                result.reason = "cancelled; hold-current-position requested"
                result.final_radians = self.latest_angle or 0.0
                self.emit(goal, "feedback", "cancelled", result.reason)
                return result
            if time.monotonic() - last_authority_check >= 0.2:
                last_authority_check = time.monotonic()
                check = ControlAuthority.Request()
                check.operation = "status"
                check.run_id = goal.run_id
                check.lease_id = goal.lease_id
                if not self.control.wait_for_service(timeout_sec=0.2):
                    active = False
                else:
                    check_future = self.control.call_async(check)
                    check_deadline = time.monotonic() + 0.25
                    while not check_future.done() and time.monotonic() < check_deadline:
                        time.sleep(0.01)
                    active = (
                        check_future.done()
                        and check_future.result() is not None
                        and check_future.result().allowed
                        and check_future.result().lease_matches
                        and not check_future.result().estop_latched
                        and check_future.result().mode != "Disarmed"
                    )
                if not active:
                    command.data = self.latest_angle or 0.0
                    self.publisher.publish(command)
                    goal_handle.abort()
                    result.reason = "control lease, mode or supervisor status lost"
                    result.final_radians = self.latest_angle or 0.0
                    self.emit(goal, "feedback", "failed", result.reason)
                    return result
            if self.latest_angle is None or time.time_ns() - self.last_pose_wall_ns > 1_000_000_000:
                goal_handle.abort()
                result.reason = "pose feedback lost"
                self.emit(goal, "feedback", "failed", result.reason)
                return result
            if abs(self.latest_angle - goal.target_radians) < 0.05:
                goal_handle.succeed()
                result.succeeded = True
                result.reason = "observed joint reached target"
                result.final_radians = self.latest_angle
                self.emit(goal, "feedback", "completed", result.reason)
                return result
            error_radians = goal.target_radians - self.latest_angle
            command.data = self.latest_angle + max(-0.02, min(0.02, error_radians))
            self.publisher.publish(command)
            if not dispatched:
                dispatched = True
                self.emit(
                    goal,
                    "action",
                    "dispatched",
                    "bounded 0.02 rad setpoint increments through ROS-Gazebo bridge",
                )
            feedback = MoveJoint.Feedback()
            feedback.current_radians = self.latest_angle
            feedback.stage = "moving"
            goal_handle.publish_feedback(feedback)
            feedback_count += 1
            if feedback_count % 10 == 1:
                self.emit(goal, "feedback", "moving", "joint angle observed from Gazebo pose")
            time.sleep(0.05)
        goal_handle.abort()
        result.reason = "simulated movement timed out"
        result.final_radians = self.latest_angle or 0.0
        self.emit(goal, "feedback", "failed", result.reason)
        return result


def main() -> None:
    rclpy.init()
    node = SimulationActionServer()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
