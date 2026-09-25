#include <chrono>
#include <cstdlib>
#include <memory>
#include <mutex>
#include <string>

#include "embodied_interfaces/srv/authorize_motion.hpp"
#include "embodied_interfaces/srv/control_authority.hpp"
#include "rclcpp/rclcpp.hpp"
#include "safety_supervisor/safety_rules.hpp"

using AuthorizeMotion = embodied_interfaces::srv::AuthorizeMotion;
using ControlAuthority = embodied_interfaces::srv::ControlAuthority;

static uint64_t NowWallMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

static std::string RunId() {
  const char* configured = std::getenv("RUN_ID");
  return configured == nullptr ? "" : configured;
}

class SafetySupervisor final : public rclcpp::Node {
 public:
  SafetySupervisor() : Node("simulation_safety_supervisor"), authority_(RunId()) {
    control_service_ = create_service<ControlAuthority>(
        "/simulation/control_authority",
        [this](const std::shared_ptr<ControlAuthority::Request> request,
               std::shared_ptr<ControlAuthority::Response> response) {
          std::lock_guard<std::mutex> lock(mutex_);
          const uint64_t now_ms = NowWallMs();
          const auto decision = authority_.Apply(
              request->operation, request->run_id, request->lease_id, request->actor_id,
              request->requested_mode, request->ttl_seconds, request->confirmed, now_ms);
          response->allowed = decision.allowed;
          response->mode = authority_.mode();
          response->estop_latched = authority_.estop_latched();
          response->lease_matches = authority_.LeaseActive(now_ms) &&
                                    request->lease_id == authority_.lease_id();
          response->lease_owner = authority_.LeaseActive(now_ms) ? authority_.lease_owner() : "";
          response->lease_id = decision.allowed && request->operation == "acquire"
                                   ? authority_.lease_id()
                                   : "";
          response->expires_at_wall_ms = authority_.expires_at_wall_ms();
          response->reason = decision.reason;
        });
    service_ = create_service<AuthorizeMotion>(
        "/simulation/authorize_motion",
        [this](const std::shared_ptr<AuthorizeMotion::Request> request,
               std::shared_ptr<AuthorizeMotion::Response> response) {
          std::lock_guard<std::mutex> lock(mutex_);
          const auto decision = authority_.Authorize(
              {request->run_id, request->robot_id, request->joint_name,
               request->target_radians, request->command_sequence, request->correlation_id,
               request->lease_id},
              last_sequence_, NowWallMs());
          response->allowed = decision.allowed;
          response->reason = decision.reason;
          if (decision.allowed) {
            last_sequence_ = request->command_sequence;
          }
          RCLCPP_INFO(get_logger(), "authorization sequence=%lu allowed=%s reason=%s",
                      request->command_sequence, response->allowed ? "true" : "false",
                      response->reason.c_str());
        });
  }

 private:
  uint64_t last_sequence_{0};
  safety_supervisor::AuthorityState authority_;
  std::mutex mutex_;
  rclcpp::Service<ControlAuthority>::SharedPtr control_service_;
  rclcpp::Service<AuthorizeMotion>::SharedPtr service_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SafetySupervisor>());
  rclcpp::shutdown();
  return 0;
}
