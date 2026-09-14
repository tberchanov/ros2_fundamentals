#! /usr/bin/env python3
 
"""
Description:
    This ROS 2 node periodically publishes "Hello World" messages on a topic.
    It demonstrates basic ROS concepts such as node creation, publishing, and
    timer usage.
-------
Publishing Topics:
    The channel containing the "Hello World" messages
    /py_example_topic - std_msgs/String
    The channel containing the battery level messages
    /py_example_battery_topic - sensor_msgs/BatteryState
-------
Subscription Topics:
    None
-------
Author: Addison Sears-Collins
Date: November 4, 2024
"""

import rclpy  # Import the ROS 2 client library for Python
from rclpy.node import Node  # Import the Node class for creating ROS 2 nodes

from std_msgs.msg import String  # Import the String message type for publishing
from sensor_msgs.msg import BatteryState  # Import the BatteryState message type for publishing


class MinimalPyPublisher(Node):
    """Create MinimalPyPublisher node.

    """

    def __init__(self):
        """ Create a custom node class for publishing messages

        """

        # Initialize the node with a name
        super().__init__('minimal_py_publisher')

        # Creates a publisher on the topic "topic" with a queue size of 10 messages
        self.publisher_1 = self.create_publisher(String, '/py_example_topic', 10)

        # Creates a publisher for the battery level topic
        self.publisher_2 = self.create_publisher(BatteryState, '/py_example_battery_topic', 10)

        # Create a timer with a period of 0.5 seconds to trigger the callback function
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Create a timer with a period of 1.0 seconds to trigger the battery callback
        battery_timer_period = 1.0  # seconds
        self.battery_timer = self.create_timer(battery_timer_period, self.battery_timer_callback)

        # Initialize a counter variable for message content
        self.i = 0

        # Initialize the battery level (charge percentage, in the 0.0-1.0 range)
        self.battery_level = 0.0

    def timer_callback(self):
        """Callback function executed periodically by the timer.

        """
        # Create a new String message object
        msg = String()

        # Set the message data with a counter
        msg.data = 'Hello World: %d' % self.i

        # Publish the message on the topic
        self.publisher_1.publish(msg)

        # Log a message indicating that the message has been published
        self.get_logger().info('Publishing: "%s"' % msg.data)

        # Increment the counter for the next message
        self.i = self.i + 1

    def battery_timer_callback(self):
        """Callback function executed periodically by the battery timer.

        """
        # Create a new BatteryState message object
        msg = BatteryState()

        # Stamp the message with the current time
        msg.header.stamp = self.get_clock().now().to_msg()

        # Set the charge percentage (0.0 to 1.0) with the current battery level
        msg.percentage = self.battery_level

        # Mark the battery as charging so the percentage increasing makes sense
        msg.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_CHARGING

        # Publish the message on the topic
        self.publisher_2.publish(msg)

        # Log a message indicating that the message has been published
        self.get_logger().info('Publishing battery percentage: "%.2f"' % msg.percentage)

        # Increment the battery level for the next message, wrapping at 1.0
        self.battery_level = (self.battery_level + 0.01) % 1.01
 
 
def main(args=None):
    """Main function to start the ROS 2 node.
 
    Args:
        args (List, optional): Command-line arguments. Defaults to None.
    """
 
    # Initialize ROS 2 communication
    rclpy.init(args=args)
 
    # Create an instance of the MinimalPublisher node
    minimal_py_publisher = MinimalPyPublisher()
 
    # Keep the node running and processing events.
    rclpy.spin(minimal_py_publisher)
 
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_py_publisher.destroy_node()
 
    # Shutdown ROS 2 communication
    rclpy.shutdown()
 
 
if __name__ == '__main__':
    # Execute the main function if the script is run directly
    main()