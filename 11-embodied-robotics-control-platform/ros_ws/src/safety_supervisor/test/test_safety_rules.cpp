#include <limits>

#include "gtest/gtest.h"
#include "safety_supervisor/safety_rules.hpp"

using safety_supervisor::Authorize;
using safety_supervisor::MotionCommand;

TEST(SimulationSafety, AuthorizesBoundedMonotonicTarget) {
  MotionCommand command{"studio-local", "embodied_demo", "left_shoulder", 0.4, 1, "trace-1"};
  EXPECT_TRUE(Authorize(command, 0, "studio-local").allowed);
  EXPECT_FALSE(Authorize(command, 1, "studio-local").allowed);
}

TEST(SimulationSafety, RejectsOutOfRangeNonFiniteAndWrongScope) {
  MotionCommand command{"studio-local", "embodied_demo", "left_shoulder", 1.1, 1, "trace-1"};
  EXPECT_FALSE(Authorize(command, 0, "studio-local").allowed);
  command.target_radians = std::numeric_limits<double>::quiet_NaN();
  EXPECT_FALSE(Authorize(command, 0, "studio-local").allowed);
  command.target_radians = 0.4;
  command.run_id = "other-run";
  EXPECT_FALSE(Authorize(command, 0, "studio-local").allowed);
  command.run_id = "studio-local";
  command.correlation_id.clear();
  EXPECT_FALSE(Authorize(command, 0, "studio-local").allowed);
}
