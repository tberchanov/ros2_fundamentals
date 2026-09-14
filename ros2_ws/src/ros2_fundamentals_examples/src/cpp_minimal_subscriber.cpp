#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "sensor_msgs/msg/battery_state.hpp"

class MinimalCppSubscriber : public rclcpp::Node
{
public:
    MinimalCppSubscriber() : Node("minimal_cpp_subscriber")
    {
        subscription_ = create_subscription<std_msgs::msg::String>(
            "/cpp_example_topic",
            10,
            std::bind(&MinimalCppSubscriber::topicCallback, this, std::placeholders::_1)
        );

        battery_subscription_ = create_subscription<sensor_msgs::msg::BatteryState>(
            "/cpp_example_battery_topic",
            10,
            std::bind(&MinimalCppSubscriber::batteryTopicCallback, this, std::placeholders::_1)
        );
    }

    void topicCallback(const std_msgs::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(get_logger(), "I heard: '%s'", msg->data.c_str());
    }

    void batteryTopicCallback(const sensor_msgs::msg::BatteryState::SharedPtr msg)
    {
        RCLCPP_INFO(get_logger(), "I heard battery percentage: '%.2f'", msg->percentage);
    }

private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
    rclcpp::Subscription<sensor_msgs::msg::BatteryState>::SharedPtr battery_subscription_;

};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MinimalCppSubscriber>());
    rclcpp::shutdown();
    return 0;
}