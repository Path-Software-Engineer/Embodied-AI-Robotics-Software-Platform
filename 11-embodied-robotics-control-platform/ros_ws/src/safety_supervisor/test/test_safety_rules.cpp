#include <limits>

#include "gtest/gtest.h"
#include "safety_supervisor/safety_rules.hpp"

using safety_supervisor::AuthorityState;
using safety_supervisor::MotionCommand;

TEST(SimulationSafety, RequiresExclusiveArmedLeaseForMotion) {
  AuthorityState supervisor("studio-local");
  MotionCommand command{"studio-local", "embodied_demo", "left_shoulder", 0.4, 1,
                        "trace-1", "lease-1"};
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1000).allowed);
  EXPECT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-1", "operator-1", "", 10,
                               false, 1000).allowed);
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1000).allowed);
  EXPECT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual", 0,
                               true, 1000).allowed);
  EXPECT_TRUE(supervisor.Authorize(command, 0, 1001).allowed);
  EXPECT_FALSE(supervisor.Authorize(command, 1, 1001).allowed);
  EXPECT_FALSE(supervisor.Authorize(command, 0, 11000).allowed);
}

TEST(SimulationSafety, RejectsOutOfRangeNonFiniteAndWrongScope) {
  AuthorityState supervisor("studio-local");
  ASSERT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-1", "operator-1", "", 10,
                               false, 1000).allowed);
  ASSERT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual", 0,
                               true, 1000).allowed);
  MotionCommand command{"studio-local", "embodied_demo", "left_shoulder", 1.1, 1,
                        "trace-1", "lease-1"};
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1001).allowed);
  command.target_radians = std::numeric_limits<double>::quiet_NaN();
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1001).allowed);
  command.target_radians = 0.4;
  command.run_id = "other-run";
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1001).allowed);
  command.run_id = "studio-local";
  command.correlation_id.clear();
  EXPECT_FALSE(supervisor.Authorize(command, 0, 1001).allowed);
}

TEST(SimulationSafety, LeaseOwnershipModeTransitionsAndLatchedEStop) {
  AuthorityState supervisor("studio-local");
  EXPECT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-1", "operator-1", "", 10,
                               false, 1000).allowed);
  EXPECT_FALSE(supervisor.Apply("acquire", "studio-local", "lease-2", "operator-2", "", 10,
                                false, 1001).allowed);
  EXPECT_FALSE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1",
                                "AutonomousSim", 0, true, 1001).allowed);
  EXPECT_FALSE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual",
                                0, false, 1001).allowed);
  EXPECT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual",
                               0, true, 1001).allowed);
  EXPECT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Assisted",
                               0, true, 1001).allowed);
  EXPECT_TRUE(supervisor.Apply("estop", "studio-local", "", "", "", 0, false, 1002).allowed);
  EXPECT_TRUE(supervisor.estop_latched());
  EXPECT_FALSE(supervisor.Apply("acquire", "studio-local", "lease-2", "operator-2", "", 10,
                                false, 1003).allowed);
  EXPECT_FALSE(supervisor.Apply("reset_estop", "studio-local", "", "operator-2", "", 0,
                                false, 1003).allowed);
  EXPECT_TRUE(supervisor.Apply("reset_estop", "studio-local", "", "operator-2", "", 0,
                               true, 1003).allowed);
  EXPECT_EQ(supervisor.mode(), "Disarmed");
}

TEST(SimulationSafety, LeaseExpiryDisarmsAndStopDoesNotClearLatch) {
  AuthorityState supervisor("studio-local");
  ASSERT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-1", "operator-1", "", 1,
                               false, 1000).allowed);
  ASSERT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual", 0,
                               true, 1001).allowed);
  MotionCommand command{"studio-local", "embodied_demo", "left_shoulder", 0.4, 1,
                        "trace-1", "lease-1"};
  EXPECT_FALSE(supervisor.Authorize(command, 0, 2000).allowed);
  EXPECT_EQ(supervisor.mode(), "Disarmed");
  EXPECT_TRUE(supervisor.Apply("estop", "studio-local", "", "", "", 0, false, 2001).allowed);
  EXPECT_FALSE(supervisor.Apply("stop", "studio-local", "lease-1", "operator-1", "", 0,
                                true, 2002).allowed);
  EXPECT_TRUE(supervisor.estop_latched());
}

TEST(SimulationSafety, StatusDisarmsExpiredLeaseAndHeartbeatRequiresOwner) {
  AuthorityState supervisor("studio-local");
  ASSERT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-1", "operator-1", "", 1,
                               false, 1000).allowed);
  ASSERT_TRUE(supervisor.Apply("mode", "studio-local", "lease-1", "operator-1", "Manual", 0,
                               true, 1001).allowed);
  EXPECT_FALSE(supervisor.Apply("heartbeat", "studio-local", "lease-1", "operator-2", "", 1,
                                false, 1500).allowed);
  EXPECT_TRUE(supervisor.Apply("heartbeat", "studio-local", "lease-1", "operator-1", "", 1,
                               false, 1500).allowed);
  EXPECT_TRUE(supervisor.Apply("status", "studio-local", "", "", "", 0,
                               false, 2000).allowed);
  EXPECT_EQ(supervisor.mode(), "Manual");
  EXPECT_TRUE(supervisor.Apply("status", "studio-local", "", "", "", 0,
                               false, 2500).allowed);
  EXPECT_EQ(supervisor.mode(), "Disarmed");
  EXPECT_FALSE(supervisor.LeaseActive(2500));
  EXPECT_TRUE(supervisor.lease_id().empty());
  EXPECT_TRUE(supervisor.Apply("acquire", "studio-local", "lease-2", "operator-2", "", 1,
                               false, 2501).allowed);
}
