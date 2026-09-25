#pragma once

#include <cmath>
#include <cstdint>
#include <string>

namespace safety_supervisor {

struct MotionCommand {
  std::string run_id;
  std::string robot_id;
  std::string joint_name;
  double target_radians;
  uint64_t sequence;
  std::string correlation_id;
};

struct Authorization {
  bool allowed;
  std::string reason;
};

inline Authorization Authorize(const MotionCommand& command, uint64_t last_sequence,
                               const std::string& expected_run_id) {
  if (expected_run_id.empty() || command.run_id != expected_run_id ||
      command.robot_id != "embodied_demo" ||
      command.joint_name != "left_shoulder") {
    return {false, "unknown simulation scope"};
  }
  if (command.correlation_id.empty()) {
    return {false, "missing correlation ID"};
  }
  if (!std::isfinite(command.target_radians) || std::abs(command.target_radians) > 0.8) {
    return {false, "joint target outside versioned limit [-0.8, 0.8] rad"};
  }
  if (command.sequence <= last_sequence) {
    return {false, "stale or duplicate command sequence"};
  }
  return {true, "authorized for configured simulation run only"};
}

}  // namespace safety_supervisor
