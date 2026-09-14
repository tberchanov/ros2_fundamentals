from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    pkg_share = FindPackageShare('gazebo_falling_box')
    gz_launch_path = PathJoinSubstitution(
        [ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py'])
    world_path = PathJoinSubstitution(
        [pkg_share, 'worlds', 'falling_box.sdf'])
    bridge_config_path = PathJoinSubstitution(
        [pkg_share, 'config', 'pressure.yaml'])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={'gz_args': ['-r ', world_path]}.items(),
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{'config_file': bridge_config_path}],
            output='screen',
        ),
        Node(
            package='gazebo_falling_box',
            executable='sensor_logger',
            output='screen',
        ),
    ])
