#!/usr/bin/env bash
set -euo pipefail
set +u
source /opt/ros/jazzy/setup.bash
source /workspace/ros_ws/install/setup.bash
set -u
export AMENT_PREFIX_PATH="/workspace/ros_ws/install/safety_supervisor:/workspace/ros_ws/install/embodied_interfaces:${AMENT_PREFIX_PATH:-}"
export PATH="/opt/ros/jazzy/opt/gz_tools_vendor/bin:$PATH"
export GZ_CONFIG_PATH="$(find /opt/ros/jazzy/opt -type d -path '*/share/gz' | paste -sd : -)"
export LD_LIBRARY_PATH="$(find /opt/ros/jazzy/opt -mindepth 2 -maxdepth 2 -type d -name lib | paste -sd : -):${LD_LIBRARY_PATH:-}"
export GZ_SIM_SYSTEM_PLUGIN_PATH="/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins"
if [[ -z "${RUN_ID:-}" ]]; then
  export RUN_ID="studio-$(date -u +%Y%m%dT%H%M%SZ)-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
fi
echo "Simulation run: ${RUN_ID} | seed=1695 | simulation-only"

gz sim -s -r --seed 1695 /workspace/sim/worlds/studio.sdf &
gazebo_pid=$!
sleep 2
if ! kill -0 "$gazebo_pid" 2>/dev/null; then
  echo "Gazebo server did not start" >&2
  exit 1
fi
ros2 run ros_gz_bridge parameter_bridge \
  '/model/embodied_demo/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V' \
  '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' \
  '/model/embodied_demo/left_shoulder/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double' &
bridge_pid=$!
ros2 run safety_supervisor safety_supervisor &
safety_pid=$!
python -m services.action_server &
action_pid=$!

trap 'kill "$action_pid" "$safety_pid" "$bridge_pid" "$gazebo_pid" 2>/dev/null || true' EXIT
python -m services.orchestrator
