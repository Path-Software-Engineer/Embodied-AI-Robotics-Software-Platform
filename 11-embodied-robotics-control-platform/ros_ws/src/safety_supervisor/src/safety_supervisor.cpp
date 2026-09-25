#include <cstdlib>
#include <memory>
#include <string>

#include "embodied_interfaces/srv/authorize_motion.hpp"
#include "rclcpp/rclcpp.hpp"
#include "safety_supervisor/safety_rules.hpp"

using AuthorizeMotion = embodied_interfaces::srv::AuthorizeMotion;

class SafetySupervisor final : public rclcpp::Node {
 public:
  SafetySupervisor() : Node("simulation_safety_supervisor") {
    const char* configured = std::getenv("RUN_ID");
    expected_run_id_ = configured == nullptr ? "" : configured;
    service_ = create_service<AuthorizeMotion>(
        "/simulation/authorize_motion",
        [this](const std::shared_ptr<AuthorizeMotion::Request> request,
               std::shared_ptr<AuthorizeMotion::Response> response) {
          const auto decision = safety_supervisor::Authorize(
              {request->run_id, request->robot_id, request->joint_name,
               request->target_radians, request->command_sequence, request->correlation_id},
              last_sequence_, expected_run_id_);
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
  std::string expected_run_id_;
  rclcpp::Service<AuthorizeMotion>::SharedPtr service_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SafetySupervisor>());
  rclcpp::shutdown();
  return 0;
}
