#!/bin/bash
set -e

source /opt/ros/jazzy/setup.bash
echo "Loaded the ROS2 Jazzy environment"

if [ -f /ros2_ws/install/setup.bash ]; then
    source /ros2_ws/install/setup.bash
    echo "Loaded the workspace environment"
fi

exec "$@"
