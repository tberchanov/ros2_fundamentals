cmake_minimum_required(VERSION 3.8)
project(ros2_fundamentals_examples)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

set(dependencies
  rclcpp
  rclpy
  std_msgs
  sensor_msgs
)

include_directories(
  include
)

# Define a CMake variable named dependencies that lists all
# ROS 2 packages and other dependencies the project requires.
set(dependencies
  rclcpp
  std_msgs
  sensor_msgs
)

# Add the specified directories to the list of paths that the compiler
# uses to search for header files. This is important for C++
# projects where you have custom header files that are not located
# in the standard system include paths.
include_directories(
  include
)
 
# Tells CMake to create an executable target named minimal_cpp_publisher
# from the source file src/minimal_cpp_publisher.cpp. Also make sure CMake
# knows about the program's dependencies.
add_executable(cpp_minimal_publisher src/cpp_minimal_publisher.cpp)
ament_target_dependencies(cpp_minimal_publisher ${dependencies})

add_executable(cpp_minimal_subscriber src/cpp_minimal_subscriber.cpp)
ament_target_dependencies(cpp_minimal_subscriber ${dependencies})
 
# Copy necessary files to designated locations in the project
install (
  DIRECTORY ros2_fundamentals_examples scripts
  DESTINATION share/${PROJECT_NAME}
)
 
install(
  DIRECTORY include/
  DESTINATION include
)
 
# Install cpp executables
install(
  TARGETS
  cpp_minimal_publisher
  DESTINATION lib/${PROJECT_NAME}
)
install(
  TARGETS
  cpp_minimal_subscriber
  DESTINATION lib/${PROJECT_NAME}
)
 
# Install Python modules for import
ament_python_install_package(${PROJECT_NAME})
 
# Add this section to install Python scripts
install(
  PROGRAMS
  ros2_fundamentals_examples/py_minimal_publisher.py
  ros2_fundamentals_examples/py_minimal_subscriber.py
  DESTINATION lib/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_include_directories(include)

ament_package()
