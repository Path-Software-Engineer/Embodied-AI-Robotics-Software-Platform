cmake_minimum_required(VERSION 3.8)
project(embodied_interfaces)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotState.msg"
  "msg/LoopEvent.msg"
  "srv/AuthorizeMotion.srv"
  "srv/ControlAuthority.srv"
  "action/MoveJoint.action"
  DEPENDENCIES geometry_msgs
)
ament_package()
