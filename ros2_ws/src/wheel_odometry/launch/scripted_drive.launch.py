import os
import signal

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction,
                            RegisterEventHandler)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

# name: (default, type). The type must match the driver's declare_parameter,
# otherwise e.g. turn_angle_deg:=180 arrives as an int and the driver dies.
DRIVE_PARAMS = {
    'speed': ('0.5', float),
    'drive_time': ('4.0', float),
    'turn_rate': ('0.5', float),
    'turn_angle_deg': ('90.0', float),
    'repetitions': ('4', int),
}


def generate_launch_description():
    pkg_share = FindPackageShare('wheel_odometry')
    run = LaunchConfiguration('run')

    driver = Node(
        package='wheel_odometry',
        executable='scripted_driver',
        parameters=[{'use_sim_time': True} | {
            name: ParameterValue(LaunchConfiguration(name), value_type=value_type)
            for name, (_, value_type) in DRIVE_PARAMS.items()
        }],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'run',
            default_value='run',
            description='Name prefix for the CSVs: <run>_odom.csv and <run>_truth.csv'),
        *[DeclareLaunchArgument(name, default_value=default)
          for name, (default, _) in DRIVE_PARAMS.items()],
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, 'launch', 'wheel_odometry.launch.py'])),
            launch_arguments={'run': run}.items(),
        ),
        driver,
        # The driver exits after the stop; end the whole experiment with it, the way
        # Ctrl-C does: SIGINT to the whole process group. A Shutdown event would only
        # signal the `gz` wrapper, leaving `gz sim server` running for the next run.
        RegisterEventHandler(OnProcessExit(
            target_action=driver,
            on_exit=[OpaqueFunction(function=lambda _: os.killpg(os.getpgrp(), signal.SIGINT))],
        )),
    ])
