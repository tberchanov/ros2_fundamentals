from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    pkg_share = FindPackageShare('wheel_odometry')
    gz_launch_path = PathJoinSubstitution(
        [ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py'])
    world_path = PathJoinSubstitution(
        [pkg_share, 'worlds', 'wheel_odometry.sdf'])
    bridge_config_path = PathJoinSubstitution(
        [pkg_share, 'config', 'bridge.yaml'])

    run = LaunchConfiguration('run')

    return LaunchDescription([
        DeclareLaunchArgument(
            'run',
            default_value='run',
            description='Name prefix for the CSVs: <run>_odom.csv and <run>_truth.csv '
                        '(relative = launch dir)'),
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
            package='wheel_odometry',
            executable='odom_processor',
            parameters=[{'csv_path': [run, '_odom.csv'], 'use_sim_time': True}],
            output='screen',
        ),
        Node(
            package='wheel_odometry',
            executable='odom_processor',
            name='truth_processor',
            remappings=[('/odom', '/ground_truth')],
            parameters=[{'csv_path': [run, '_truth.csv'], 'use_sim_time': True}],
            output='screen',
        ),
    ])
