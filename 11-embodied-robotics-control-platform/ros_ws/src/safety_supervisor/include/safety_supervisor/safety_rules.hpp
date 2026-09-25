#pragma once

#include <cmath>
#include <cstdint>
#include <string>
#include <utility>

namespace safety_supervisor {

struct MotionCommand {
  std::string run_id;
  std::string robot_id;
  std::string joint_name;
  double target_radians;
  uint64_t sequence;
  std::string correlation_id;
  std::string lease_id;
};

struct Authorization {
  bool allowed;
  std::string reason;
};

class AuthorityState {
 public:
  explicit AuthorityState(std::string expected_run_id)
      : expected_run_id_(std::move(expected_run_id)) {}

  Authorization Apply(const std::string& operation, const std::string& run_id,
                      const std::string& lease_id, const std::string& actor_id,
                      const std::string& requested_mode, uint32_t ttl_seconds,
                      bool confirmed, uint64_t now_ms) {
    if (run_id != expected_run_id_ || expected_run_id_.empty()) {
      return {false, "unknown simulation run"};
    }
    ExpireLease(now_ms);
    if (operation == "status") return {true, "current supervisor state"};
    if (operation == "estop") {
      estop_latched_ = true;
      mode_ = "Disarmed";
      lease_id_.clear();
      actor_id_.clear();
      expires_at_wall_ms_ = 0;
      return {true, "emergency stop latched"};
    }
    if (operation == "acquire") {
      if (estop_latched_) return {false, "emergency stop is latched"};
      if (lease_id.empty() || actor_id.empty() || ttl_seconds == 0 || ttl_seconds > 30) {
        return {false, "invalid lease identity or TTL"};
      }
      if (LeaseActive(now_ms)) return {false, "robot already has an active control lease"};
      lease_id_ = lease_id;
      actor_id_ = actor_id;
      expires_at_wall_ms_ = now_ms + static_cast<uint64_t>(ttl_seconds) * 1000;
      mode_ = "Disarmed";
      return {true, "exclusive control lease acquired"};
    }
    if (operation == "reset_estop") {
      if (!estop_latched_ || !confirmed || actor_id.empty()) {
        return {false, "reset requires a named actor and explicit confirmation"};
      }
      estop_latched_ = false;
      return {true, "emergency stop reset; robot remains disarmed"};
    }
    if (!LeaseActive(now_ms) || lease_id != lease_id_ || actor_id != actor_id_) {
      return {false, "control lease missing, expired or owned by another actor"};
    }
    if (operation == "heartbeat") {
      if (ttl_seconds == 0 || ttl_seconds > 30) return {false, "invalid heartbeat TTL"};
      expires_at_wall_ms_ = now_ms + static_cast<uint64_t>(ttl_seconds) * 1000;
      return {true, "lease renewed"};
    }
    if (operation == "revoke" || operation == "stop") {
      mode_ = "Disarmed";
      if (operation == "revoke") {
        lease_id_.clear();
        actor_id_.clear();
        expires_at_wall_ms_ = 0;
      }
      return {true, operation == "stop" ? "controlled stop requested" : "lease revoked"};
    }
    if (operation == "mode") {
      if (!confirmed) return {false, "mode transition requires confirmation"};
      if (requested_mode == "Disarmed") {
        mode_ = requested_mode;
        return {true, "disarmed"};
      }
      const bool allowed =
          (mode_ == "Disarmed" && requested_mode == "Manual") ||
          (mode_ == "Manual" && requested_mode == "Assisted") ||
          (mode_ == "Assisted" && requested_mode == "AutonomousSim") ||
          (mode_ == "AutonomousSim" && requested_mode == "Assisted") ||
          (mode_ == "Assisted" && requested_mode == "Manual");
      if (!allowed) return {false, "forbidden mode transition"};
      mode_ = requested_mode;
      return {true, "mode transition accepted"};
    }
    return {false, "unknown authority operation"};
  }

  Authorization Authorize(const MotionCommand& command, uint64_t last_sequence,
                          uint64_t now_ms) {
    ExpireLease(now_ms);
    if (estop_latched_) return {false, "emergency stop is latched"};
    if (!LeaseActive(now_ms) || command.lease_id != lease_id_ || mode_ == "Disarmed") {
      mode_ = "Disarmed";
      return {false, "no armed exclusive control lease"};
    }
    if (command.run_id != expected_run_id_ || command.robot_id != "embodied_demo" ||
        command.joint_name != "left_shoulder") {
      return {false, "unknown simulation scope"};
    }
    if (command.correlation_id.empty()) return {false, "missing correlation ID"};
    if (!std::isfinite(command.target_radians) || std::abs(command.target_radians) > 0.8) {
      return {false, "joint target outside versioned limit [-0.8, 0.8] rad"};
    }
    if (command.sequence <= last_sequence) return {false, "stale or duplicate command sequence"};
    return {true, "authorized by independent simulation supervisor"};
  }

  bool LeaseActive(uint64_t now_ms) const {
    return !lease_id_.empty() && !actor_id_.empty() && now_ms < expires_at_wall_ms_;
  }
  const std::string& mode() const { return mode_; }
  bool estop_latched() const { return estop_latched_; }
  const std::string& lease_id() const { return lease_id_; }
  const std::string& lease_owner() const { return actor_id_; }
  uint64_t expires_at_wall_ms() const { return expires_at_wall_ms_; }

 private:
  void ExpireLease(uint64_t now_ms) {
    if (!lease_id_.empty() && now_ms >= expires_at_wall_ms_) {
      mode_ = "Disarmed";
      lease_id_.clear();
      actor_id_.clear();
      expires_at_wall_ms_ = 0;
    }
  }

  std::string expected_run_id_;
  std::string lease_id_;
  std::string actor_id_;
  std::string mode_{"Disarmed"};
  uint64_t expires_at_wall_ms_{0};
  bool estop_latched_{false};
};

}  // namespace safety_supervisor
